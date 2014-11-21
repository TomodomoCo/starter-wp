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
# PLEASE READ THIS:
# This is not perfect. It should not be let loose on untrusted config input yet. Be careful with your YAML, sir.
# You are at your own risk. It works for me on dev -> staging.

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

pid = os.getpid()
pid_str = str(pid)

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

print "Running a mysqldump on the source (" + source_stage + ") database..."

sdump = Popen(['ssh', '-p', ssh_ports[source_stage], '-l', users[source_stage], ips[source_stage], 'mysqldump -h ' + source_host + ' -u ' + source_user + ' -p' + source_pass + ' ' + source_db + ' > ~/push_db_to_stage_' + pid_str + '_src_tmp.sql'], universal_newlines=True)

sdump.communicate()

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
sdump = Popen(['ssh', '-p', ssh_ports[source_stage], '-l', users[source_stage], ips[source_stage], 'rm -fv -- ~/push_db_to_stage_' + pid_str + '_src_tmp.sql'], universal_newlines=True)

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
