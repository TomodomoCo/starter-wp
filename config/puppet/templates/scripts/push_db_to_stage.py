#!/usr/bin/env python
#
#
# Push the current database to stage
#
# This script pushes the content in the site database for the current 
# stage to another stage, for example, development -> staging.
#
# It automatically handles the rewriting of key WordPress options siteurl,
# home and upload_path, as well as rewriting content URLs.
#
#
# Requires PyYAML for DB credentials import and Python-MySQL for string escaping
#
# Assumes Puppet, or deploy:setup has already created the DBs and populated the priv tables with the username/passwords
# specified in database.yml.
#
#

import yaml
import os
import sys
from sys import exit
import subprocess
from subprocess import Popen, PIPE, STDOUT
import _mysql
from pprint import pprint
import argparse
from pipes import quote
from datetime import datetime
import re

ips = {}
ssh_ports = {}
users = {}
passwords = {}
siteurls = {}
homes = {}
upload_paths = {}
upload_url_paths = {}
tbl_prefixes = {}

# argument parsing
parser = argparse.ArgumentParser(description='Command line arguments')
parser.add_argument('-d', '--database-config', default='config/database.yml', help='The path to the database.yml file. (Default: %(default)s)')
parser.add_argument('-p', '--project-config', default='config/project.yml', help='The path to the project.yml file. (Default: %(default)s)')
parser.add_argument('--ignore-upload-paths', action='store_true', help='Do not change the upload_path, upload_url_path, siteurl or home after the database is synced. (Default: %(default)s)')
parser.add_argument('--update-site-paths', action='store_true', help='Update the siteurl and home paths in the database, after it is synced. (Default %(default)s)')
parser.add_argument('-f', '--from', help='The stage from which to download the database.')
parser.add_argument('-t', '--to', help='The stage whose database should be replaced.', action='append')
parser.add_argument('--days', default=0, help='Transfer only the last n days of posts and related content. (Default: %(default)s, where 0 transfers all posts.)')
parser.add_argument('--source-prefix-override', default=None, help='Force the source database table prefix to the specified prefix. Useful with WP Multisite')
arguments = parser.parse_args()


db_config_path = arguments.database_config
proj_config_path = arguments.project_config
ignore_upload_paths = arguments.ignore_upload_paths
update_site_paths = arguments.update_site_paths

should_ignore_upload_paths = {}

source_stage = vars(arguments)["from"] # hack, because 'from' is reserved, so we can't access it via the Namespace
dest_stage = arguments.to

if not source_stage or not dest_stage or len(source_stage) < 1 or len(dest_stage) < 1:
	parser.print_help()
	exit(2)

try:
        days = int(arguments.days)
except ValueError as e:
        parser.print_help()
        exit(2)

if days < 0:
        print "--days must be greater than or equal to 0."
        print
        parser.print_help()
        exit(2)


pid = os.getpid()
pid_str = str(pid) + '_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

# bring in WordPress and stage settings from project.yml
try:
        proj_config_file = open(proj_config_path, 'r')
except IOError as e:

        print "Could not open project configuration file from " + proj_config_path + "."
        print "I/O Error({0}): {1}".format(e.errno, e.strerror)
        print "Cannot continue."
        exit(1)

try:
        proj_config = yaml.safe_load(proj_config_file)
except yaml.YAMLError as e:
        print "Unable to parse project configuration file."
        print "YAMLError({0}): {1}".format(e.errno, e.strerror)
        exit(1)

if not 'stage' in proj_config:
	print "The YAML file did not seem to have a 'stage' section."
	exit(1)

if not source_stage in proj_config['stage']:
	print "The '" + source_stage + "' stage was not specified in the project configuration file's 'stage' section."
	exit(1)

for this_dest in dest_stage:
	if not this_dest in proj_config['stage']:
		print "The '" + this_dest + "' stage was not specified in the project configuration file's 'stage' section."
		exit(1)

all_stages = [source_stage] + dest_stage

for stage in all_stages:
	# sanity check the stage in the YAML
	if not 'ip' in proj_config['stage'][stage] or not 'ssh_port' in proj_config['stage'][stage] or not 'user' in proj_config['stage'][stage]:
		print "The '" + stage + "' stage in the 'stage' section of the project configuration file does not have one or more of the required 'ip', 'ssh_port' or 'user'  entries."
		exit(1)

	# load the YAML vars into our internal vars
	ips[stage] = proj_config['stage'][stage]['ip']
	ssh_ports[stage] = str(proj_config['stage'][stage]['ssh_port'])
	users[stage] = proj_config['stage'][stage]['user']
	
	# prepare some possible prefixes for the paths in case we want them
	if stage == 'production':
		url_prefix = 'www'
	else:
		url_prefix = stage

	if stage == 'dev':
		upload_url_path_prefix = 'uploads'
	else:
		upload_url_path_prefix = 'static'

	upload_path_prefix = 'uploads'

	if not ignore_upload_paths:

		# check for presence of upload paths for this stage in the project.yml
		if 'upload_path' in proj_config['stage'][stage] and 'upload_url_path' in proj_config['stage'][stage]:
			if proj_config['stage'][stage]['upload_path'] is None or proj_config['stage'][stage]['upload_url_path'] is None or len(proj_config['stage'][stage]['upload_path']) == 0 or len(proj_config['stage'][stage]['upload_url_path']) == 0:
				ignore_upload_paths = True
				print "WARNING: The '" + stage + "' stage had an upload_path and upload_url_path, but at least one was blank."
				print "The upload paths in the restored database on '" + stage + "' will be left alone."
				print ""
				should_ignore_upload_paths[stage] = True
			else:
				upload_paths[stage] = proj_config['stage'][stage]['upload_path']
				upload_url_paths[stage] = proj_config['stage'][stage]['upload_url_path']
				should_ignore_upload_paths[stage] = False

		else:
			# not set, so infer some WordPress-y type things from YAML and our sensible defaults

			print "INFO: The '" + stage + "' stage did not specify an upload_path and upload_url_path. We will assume some sensible wpframe defaults."

			upload_paths[stage] = '../../../../../' + upload_path_prefix + '.' + proj_config['domain'] + '/content/uploads'
			upload_url_paths[stage] = 'http://' + upload_url_path_prefix + '.' + proj_config['domain'] + '/content/uploads'

	else:

		should_ignore_upload_paths[stage] = True

	if update_site_paths:
		homes[stage] = 'http://' + url_prefix + '.' + proj_config['domain'] + '/'
		siteurls[stage] = 'http://' + url_prefix + '.' + proj_config['domain'] + '/wp'
		

# bring in database credentials from YAML
try:
        db_config_file = open(db_config_path, 'r')
except IOError as e:

        print "Could not open database configuration file from " + db_config_path + "."
        print "I/O Error({0}): {1}".format(e.errno, e.strerror)
        print "Cannot continue."
        exit(1)

try:
        db_config = yaml.safe_load(db_config_file)
except yaml.YAMLError as e:
        print "Unable to parse database configuration file."
        print "YAMLError({0}): {1}".format(e.errno, e.strerror)
	exit(1)

# sanity checking of config YAML
if not source_stage in db_config:
        print "The '" + source_stage + "' stage was not found in the database config YAML file."
        exit(1)
for this_dest in dest_stage:
	if not this_dest in db_config:
		print "The '" + this_dest + "' stage was not found in the database config YAML file."        
		exit(1)
for stage in all_stages:
	if not 'name' in db_config[stage] or not 'user' in db_config[stage] or not 'password' in db_config[stage] or not 'host' in db_config[stage] or not 'grant_to' in db_config[stage] or not 'tbl_prefix' in db_config[stage] or not 'host' in db_config[stage]:
		print "The '" + stage + "' stage does not have all of the required YAML attributes in the config file."
		print "Does it have the 'tbl_prefix' and 'host' in addition to the previously required attributes?"
		exit(1)
	tbl_prefixes[stage] = db_config[stage]['tbl_prefix']


if arguments.source_prefix_override is not None:
    tbl_prefixes[source_stage] = arguments.source_prefix_override
    print "INFO: Source table prefix is overriden to '" + arguments.source_prefix_override + "'. Ensure this includes a trailing underscore if appropriate!"
    print


source_db_prefix = source_stage[0] + "_"
dest_db_prefix = dest_stage[0] + "_"


# get confirmation from the user
confirm = raw_input("Are you sure you want to download the '" + source_stage + "' database and push it to '" + ", ".join(dest_stage) + "'? (y/n): ")

if not confirm == 'y' and not confirm == 'Y':
	print "Exiting as requesting."
	exit(1)


# connect to source
source_db = _mysql.escape_string(db_config[source_stage]['name'])
source_user = _mysql.escape_string(db_config[source_stage]['user'])
source_pass = quote(db_config[source_stage]['password'])
source_host = _mysql.escape_string(db_config[source_stage]['host'])

# mysqldump the source

# simple method for days=0
if days == 0:
    print "Running a simple mysqldump on the source (" + source_stage + ") database..."

    sdump = Popen(['ssh', '-p', ssh_ports[source_stage], '-l', users[source_stage], ips[source_stage], 'mysqldump -h ' + source_host + ' -u ' + source_user + ' -p' + source_pass + ' ' + source_db + ' > ~/push_db_to_stage_' + pid_str + '_src_tmp.sql'], universal_newlines=True)

    sdump.communicate()

else:
    # complex method for selective dumping

    print "Running a complex dump for " + str(days) + "..."
    print


    print "Determining if this is a WPMU install..."

    # before anything else, determine if this is WPMU and we should loop over prefixes
    listtablescmd = Popen(['ssh', '-p', ssh_ports[source_stage], '-l', users[source_stage], ips[source_stage], 'mysql -Bh ' + source_host + ' -u ' + source_user + ' -p' + source_pass + ' -se "SHOW TABLES" ' + source_db + ' > ~/push_db_to_stage_' + pid_str + '_' + source_db + '_list.txt'], universal_newlines=True)
    listtablescmd.communicate()

    # pull down that list
    listtablesdump = Popen(['scp', '-C', '-P', ssh_ports[source_stage], users[source_stage] + '@' + ips[source_stage] + ':~/push_db_to_stage_' + pid_str + '_' + source_db + '_list.txt', '.'], universal_newlines=True)
    listtablesdump.communicate()
    print

    # determine if any prefix_n tables exist (e.g. wp_2_*, wp_3_*)
    dumpable_prefixes = [ tbl_prefixes[source_stage] ]
    lt = open('./push_db_to_stage_' + pid_str + '_' + source_db + '_list.txt', 'r')
    for line in lt:
      dumpable_prefix = line[: (len(tbl_prefixes[source_stage])+2)]
      #print "this dumpable prefix is " + dumpable_prefix + " from " + line
      if re.match(tbl_prefixes[source_stage] + r"([0-9]+)_", line) and dumpable_prefix not in dumpable_prefixes:
        print "INFO: Will dump the prefix " + dumpable_prefix
        dumpable_prefixes.append( dumpable_prefix ) 

    lt.close()
    
    # remove local temporary file...
    os.remove('./push_db_to_stage_' + pid_str + '_' + source_db + '_list.txt')
    
    # remove from source...
    print "Removing the temporary file from the " + source_stage + " server..."
    removesource = Popen(['ssh', '-p', ssh_ports[source_stage], '-l', users[source_stage], ips[source_stage], 'rm -fv -- ~/push_db_to_stage_' + pid_str + '_' + source_db + '_list.txt'], universal_newlines=True)
    removesource.communicate()

    print

    # determine number of posts that will be pulled from each prefix
    for this_prefix in dumpable_prefixes:
      print
      print "INFO: This dump of " + str(days) + " days of " + this_prefix + "* will have the following number of posts (includes revisions, drafts):"

      postnumcmd = Popen(['ssh', '-qp', ssh_ports[source_stage], '-l', users[source_stage], ips[source_stage], 'mysql -t -Bh ' + source_host + ' -u ' + source_user + ' -p' + source_pass + ' ' + source_db + ' -e "SELECT COUNT(ID) AS posts_subset_count FROM ' + this_prefix + 'posts WHERE post_modified_gmt > (NOW() - INTERVAL ' + str(days) + ' DAY);" '], universal_newlines=True)
      postnumcmd.communicate()

    # get confirmation from the user
    confirm = raw_input("Are you sure you want to replace the data on '" + ", ".join(dest_stage) + "' with this subset of posts? (y/n): ")
    if not confirm == 'y' and not confirm == 'Y':
	print "Exiting as requesting."
	exit(1)

    for this_prefix in dumpable_prefixes:
      # selectively dump the wp_posts table
      print "Dumping " + this_prefix + "posts..."
      wpposts = Popen(['ssh', '-p', ssh_ports[source_stage], '-l', users[source_stage], ips[source_stage], 'mysqldump --single-transaction -h ' + source_host + ' -u ' + source_user + ' -p' + source_pass + ' ' + source_db + ' ' + this_prefix + 'posts --where="post_modified_gmt > ( NOW() - INTERVAL ' + str(days) + ' DAY)" > ~/push_db_to_stage_' + pid_str + '_' + this_prefix + '_posts_src_tmp.sql'], universal_newlines=True)
      wpposts.communicate()

      # selectively dump wp_postmeta
      print "Dumping " + this_prefix + "postmeta..."
      wppostmeta = Popen(['ssh', '-p', ssh_ports[source_stage], '-l', users[source_stage], ips[source_stage], 'mysqldump --single-transaction -h ' + source_host + ' -u ' + source_user + ' -p' + source_pass + ' ' + source_db + ' ' + this_prefix + 'postmeta --where="post_id IN (SELECT ID FROM ' + this_prefix + 'posts WHERE post_modified_gmt > ( NOW() - INTERVAL ' + str(days) + ' DAY))" > ~/push_db_to_stage_' + pid_str + '_' + this_prefix + '_postmeta_src_tmp.sql'], universal_newlines=True)
      wppostmeta.communicate()

      # selectively dump wp_comments
      print "Dumping " + this_prefix + "comments..."
      wpcomments = Popen(['ssh', '-p', ssh_ports[source_stage], '-l', users[source_stage], ips[source_stage], 'mysqldump --single-transaction -h ' + source_host + ' -u ' + source_user + ' -p' + source_pass + ' ' + source_db + ' ' + this_prefix + 'comments --where="comment_post_id IN (SELECT ID FROM ' + this_prefix + 'posts WHERE post_modified_gmt > ( NOW() - INTERVAL ' + str(days) + ' DAY))" > ~/push_db_to_stage_' + pid_str + '_' + this_prefix + '_comments_src_tmp.sql'], universal_newlines=True)
      wpcomments.communicate()

      # selectively dump wp_commentmeta
      print "Dumping " + this_prefix + "commentmeta..."
      wpcommentmeta = Popen(['ssh', '-p', ssh_ports[source_stage], '-l', users[source_stage], ips[source_stage], 'mysqldump --single-transaction -h ' + source_host + ' -u ' + source_user + ' -p' + source_pass + ' ' + source_db + ' ' + this_prefix + 'commentmeta --where="comment_id IN (SELECT comment_post_ID FROM ' + this_prefix + 'comments AS wpc INNER JOIN ' + this_prefix + 'posts AS wpp ON wpp.ID = wpc.comment_post_ID WHERE wpp.post_modified_gmt > ( NOW() - INTERVAL ' + str(days) + ' DAY))" > ~/push_db_to_stage_' + pid_str + '_' + this_prefix + '_commentmeta_src_tmp.sql'], universal_newlines=True)
      wpcommentmeta.communicate()

      # selectively dump wp_term_relationships
      print "Dumping " + this_prefix + "term_relationships..."
      wpterm_relationships = Popen(['ssh', '-p', ssh_ports[source_stage], '-l', users[source_stage], ips[source_stage], 'mysqldump --single-transaction -h ' + source_host + ' -u ' + source_user + ' -p' + source_pass + ' ' + source_db + ' ' + this_prefix + 'term_relationships --where="object_id IN (SELECT ID FROM ' + this_prefix + 'posts AS wpp WHERE wpp.post_modified_gmt > ( NOW() - INTERVAL ' + str(days) + ' DAY))" > ~/push_db_to_stage_' + pid_str + '_' + this_prefix + '_term_relationships_src_tmp.sql'], universal_newlines=True)
      wpterm_relationships.communicate()


      print
      print "INFO: It is safe to ignore warnings about " + this_prefix + "cfs_values being missing if CFS is not installed in this site."

      print "Dumping " + this_prefix + "cfs_values..."
      # selectively dump wp_cfs_values
      wpcfs_values = Popen(['ssh', '-p', ssh_ports[source_stage], '-l', users[source_stage], ips[source_stage], 'mysqldump --single-transaction -h ' + source_host + ' -u ' + source_user + ' -p' + source_pass + ' ' + source_db + ' ' + this_prefix + 'cfs_values --where="post_id IN (SELECT ID FROM ' + this_prefix + 'posts AS wpp WHERE wpp.post_modified_gmt > ( NOW() - INTERVAL ' + str(days) + ' DAY))" > ~/push_db_to_stage_' + pid_str + '_' + this_prefix + '_cfs_values_src_tmp.sql'], universal_newlines=True)
      wpcfs_values.communicate()

      # dump other tables

      # tables dump subquery for listing tables to dump -- we exclude the separate ones we have done
      ignore_tables = [ 'posts', 'postmeta', 'comments', 'commentmeta', 'term_relationships', 'cfs_values' ]
      ignore_tables_formatted = ''

      for table in ignore_tables:
	      ignore_tables_formatted += '\'' + this_prefix + table + '\','

      ignore_tables_formatted = ignore_tables_formatted[:-1] # cut off last comma

      # our tables dump subquery must exclude any tables that match another prefix (wp_* matches the wp_n_* 'other' tables, which is not desired)
      if tbl_prefixes[source_stage] == this_prefix:
        other_prefixes = list(dumpable_prefixes)
	# remove this prefix from other_prefixes list
	if this_prefix in other_prefixes:
	  other_prefixes.remove(this_prefix)

	other_prefixes_formatted = ' AND TABLE_NAME NOT LIKE '

	for other_prefix in other_prefixes:
	  other_prefixes_formatted += '\'' + other_prefix + '%\' AND TABLE_NAME NOT LIKE '

	other_prefixes_formatted = other_prefixes_formatted[:-25] # cut off last 'AND' to finish statement
      else:
        other_prefixes_formatted = ''

      # this subquery selects which tables specifically for mysqldump to dump below
      tables_subquery = 'mysql -h ' + source_host + ' -u ' + source_user + ' -p' + source_pass + ' -Bse "SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA=\'' + source_db + '\' AND TABLE_NAME LIKE \'' + this_prefix + '%\' AND TABLE_NAME NOT IN (' + ignore_tables_formatted + ')' + other_prefixes_formatted + '"'
      #print tables_subquery
      
      # actually do the 'other' tables dump
      print "Dumping " + this_prefix + "'s other tables..."
      sdump = Popen(['ssh', '-p', ssh_ports[source_stage], '-l', users[source_stage], ips[source_stage], 'mysqldump -h ' + source_host + ' -u ' + source_user + ' -p' + source_pass + ' ' + source_db + ' --tables $(' + tables_subquery + ') > ~/push_db_to_stage_' + pid_str + '_' + this_prefix + '_other_tmp.sql'], universal_newlines=True)
      sdump.communicate() 

      print "Completed processing " + this_prefix
      print "--------------------------"
      print


    print "Merging dumps..."
    # merge dumps
    mergedumps = Popen(['ssh', '-p', ssh_ports[source_stage], '-l', users[source_stage], ips[source_stage], 'cat ~/push_db_to_stage_' + pid_str + '*.sql > ~/push_db_to_stage_' + pid_str + '_src_tmp.sql'], universal_newlines=True)
    mergedumps.communicate() 

print "Done."
print

# download the file
print "Downloading the dump..."

sdump = Popen(['scp', '-C', '-P', ssh_ports[source_stage], users[source_stage] + '@' + ips[source_stage] + ':~/push_db_to_stage_' + pid_str + '_src_tmp.sql', '.'], universal_newlines=True)
sdump.communicate()

print "Done."
print

# remove from source
print "Removing the temporary file from the " + source_stage + " server..."
sdump = Popen(['ssh', '-p', ssh_ports[source_stage], '-l', users[source_stage], ips[source_stage], 'rm -fv -- ~/push_db_to_stage_' + pid_str + '*.sql'], universal_newlines=True)

sdump.communicate()


print "Done."
print

for this_dest in dest_stage:

	# get confirmation from the user
	confirm = raw_input("This is your final stop before the push of the database to '" + this_dest + "'. Do you want to go ahead? (y/n): ")

	if not confirm == 'y' and not confirm == 'Y':
        	print "Exiting as requesting."
        	exit(1)

	print "Uploading the source (" + source_stage + ") database dump to " + this_dest + "..."
	print
	ddump = Popen(['scp', '-C', '-P', ssh_ports[this_dest], './push_db_to_stage_' + pid_str + '_src_tmp.sql', users[this_dest] + '@' + ips[this_dest] + ':~/push_db_to_stage_' + pid_str + '_dest_tmp.sql'], universal_newlines=True)
	ddump.communicate()

	print "Done."
	print

	print "Applying the (" + source_stage + ") database dump to the database on " + this_dest + "..."
	print

	# execute against the destination
	dest_db = _mysql.escape_string(db_config[this_dest]['name'])
	dest_user = _mysql.escape_string(db_config[this_dest]['user'])
	dest_pass = quote(db_config[this_dest]['password'])
	dest_host = _mysql.escape_string(db_config[this_dest]['host'])

	dexec = Popen(['ssh', '-p', ssh_ports[this_dest], '-l', users[this_dest], ips[this_dest], 'mysql -h ' + dest_host + ' -u ' + dest_user + ' -p' + dest_pass + ' ' + dest_db + ' < ~/push_db_to_stage_' + pid_str + '_dest_tmp.sql'], universal_newlines=True)

	dexec.communicate()


	print "Done."
	print

	# remove from source
	print "Removing the temporary file from the " + this_dest + " server..."
	ddump = Popen(['ssh', '-p', ssh_ports[this_dest], '-l', users[this_dest], ips[this_dest], 'rm -fv -- ~/push_db_to_stage_' + pid_str + '_dest_tmp.sql'], universal_newlines=True)
 	 
	ddump.communicate()
	print "Done."
	print

	# now, change the variables that need changing

	# get the variables ready

	sql = ""

	old_tblprefix = _mysql.escape_string(tbl_prefixes[source_stage])
	new_tblprefix = _mysql.escape_string(tbl_prefixes[this_dest])

	if not should_ignore_upload_paths[this_dest]:
		old_upload_url_path = _mysql.escape_string(upload_url_paths[source_stage])
		new_upload_url_path = _mysql.escape_string(upload_url_paths[this_dest])
		old_upload_path = _mysql.escape_string(upload_paths[source_stage])
		new_upload_path = _mysql.escape_string(upload_paths[this_dest])
		
		sql = sql + "UPDATE `" + new_tblprefix + "posts` SET post_content = REPLACE(post_content, '" + old_upload_url_path + "', '" + new_upload_url_path + "');\n\
	UPDATE `" + new_tblprefix + "options` SET option_value = '" + new_upload_path + "' WHERE option_name = 'upload_path';\n\
	UPDATE `" + new_tblprefix + "options` SET option_value = '" + new_upload_url_path + "' WHERE option_name = 'upload_url_path';\n"

	if update_site_paths: 
		old_siteurl = _mysql.escape_string(siteurls[source_stage])
		new_siteurl = _mysql.escape_string(siteurls[this_dest])
		old_home = _mysql.escape_string(homes[source_stage])
		new_home = _mysql.escape_string(homes[this_dest])

		# sub into the MySQL commands
		sql = sql + "UPDATE `" + new_tblprefix + "options` SET option_value = '" + new_siteurl + "' WHERE option_name = 'siteurl';\n\
	UPDATE `" + new_tblprefix + "options` SET option_value = '" + new_home + "' WHERE option_name = 'home';\n\
	"

	if len(sql) > 0:
		# write this to a file, which we will then upload and execute against the destination database
		sql_file = open('./push_db_to_stage_' + pid_str + '_update_tmp.sql', 'w')
		sql_file.write(sql)
		sql_file.close()

		# upload the SQL commands for update
		print "Uploading the SQL commands for updating static content URLs..."
		sqdump = Popen(['scp', '-C', '-P', ssh_ports[this_dest], './push_db_to_stage_' + pid_str + '_update_tmp.sql', users[this_dest] + '@' + ips[this_dest] + ':~/push_db_to_stage_' + pid_str + '_update_tmp.sql'], universal_newlines=True)

		sqdump.communicate()
		print "Done."
		print

		# execute those commands
		print "Executing the update..."
		uexec =  Popen(['ssh', '-p', ssh_ports[this_dest], '-l', users[this_dest], ips[this_dest], 'mysql -h ' + dest_host + ' -u ' + dest_user + ' -p' + dest_pass + ' ' + dest_db + ' < ~/push_db_to_stage_' + pid_str + '_update_tmp.sql'], universal_newlines=True)

		update_result = uexec.communicate()

		print "Done."
		print

		# remove from source
		print "Removing the temporary file from the " + this_dest + " server..."
		udump = Popen(['ssh', '-p', ssh_ports[this_dest], '-l', users[this_dest], ips[this_dest], 'rm -fv -- ~/push_db_to_stage_' + pid_str + '_update_tmp.sql'], universal_newlines=True)
 	 
		udump.communicate()
		print "Done."
		print


# remove local temporary files
print "Removing local temporary files..."
if len(sql) > 0:
	os.remove('./push_db_to_stage_' + pid_str + '_update_tmp.sql')

os.remove('./push_db_to_stage_' + pid_str + '_src_tmp.sql')

print
print "All done!"
