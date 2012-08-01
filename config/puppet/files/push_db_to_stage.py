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

ips = {}
ssh_ports = {}
users = {}
passwords = {}
siteurls = {}
homes = {}
upload_paths = {}
upload_url_paths = {}

# argument parsing
parser = argparse.ArgumentParser(description='Command line arguments')
parser.add_argument('source_stage', help='The stage from which to download the database.')
parser.add_argument('dest_stage', help='The stage whose database should be replaced.')
parser.add_argument('-d', '--database-config', default='config/database.yml', help='The path to the database.yml file. (Default: %(default)s)')
parser.add_argument('-p', '--project-config', default='config/project.yml', help='The path to the project.yml file. (Default: %(default)s)')
arguments = parser.parse_args()


db_config_path = arguments.database_config
proj_config_path = arguments.project_config

source_stage = arguments.source_stage
dest_stage = arguments.dest_stage

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

# bring in tbl_prefix
if not 'tbl_prefix' in proj_config['application']:
	print "The tbl_prefix was not found in the project configuration file."
	exit(1)
tbl_prefix = proj_config['application']['tbl_prefix']

# begin to bring in servers stuff
if not 'servers' in proj_config['application']:
	print "The servers section was not found in the project configuration file."
	exit(1)

if not source_stage in proj_config['application']['servers']:
	print "The '" + source_stage + "' stage was not specified in the project configuration file's 'servers' section."
	exit(1)

if not dest_stage in proj_config['application']['servers']:
	print "The '" + dest_stage + "' stage was not specified in the project configuration file's 'servers' section."
	exit(1)

for stage in [source_stage, dest_stage]:
	# sanity check the stage in the YAML
	if not 'ip' in proj_config['application']['servers'][stage] or not 'port' in proj_config['application']['servers'][stage] or not 'user' in proj_config['application']['servers'][stage]:
		print "The '" + stage + "' stage in the 'servers' section of the project configuration file does not have one or more of the required 'ip', 'port' or 'user' entries."
		exit(1)

	# load the YAML vars into our internal vars
	ips[stage] = proj_config['application']['servers'][stage]['ip']
	ssh_ports[stage] = str(proj_config['application']['servers'][stage]['port'])
	users[stage] = proj_config['application']['servers'][stage]['user']

	# infer some WordPress-y type things from YAML and our sensible defaults
	if stage == 'production':
		url_prefix = 'www'
	else:
		url_prefix = stage
		
	if stage == 'dev':
		upload_url_path_prefix = 'uploads'
	else:
		upload_url_path_prefix = 'static'

	homes[stage] = 'http://' + url_prefix + '.' + proj_config['application']['domain'] + '/'
	siteurls[stage] = 'http://' + url_prefix + '.' + proj_config['application']['domain'] + '/wp'
	upload_paths[stage] = '../../../../../content/uploads'
	upload_url_paths[stage] = 'http://' + upload_url_path_prefix + '.' + proj_config['application']['domain'] + '/content/uploads'


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
if not dest_stage in db_config:
	print "The '" + dest_stage + "' stage was not found in the database config YAML file."        
	exit(1)
for stage in [source_stage, dest_stage]:
	if not 'name' in db_config[stage] or not 'user' in db_config[stage] or not 'password' in db_config[stage] or not 'host' in db_config[stage] or not 'grant_to' in db_config[stage]:
		print "The '" + stage + "' stage does not have all of the required YAML attributes in the config file."
		exit(1)


source_db_prefix = source_stage[0] + "_"
dest_db_prefix = dest_stage[0] + "_"


# get confirmation from the user
confirm = raw_input("Are you sure you want to download the '" + source_stage + "' database and push it to '" + dest_stage + "'? (y/n): ")

if not confirm == 'y' and not confirm == 'Y':
	print "Exiting as requesting."
	exit(1)


# connect to source
source_db = _mysql.escape_string(db_config[source_stage]['name'])
source_user = _mysql.escape_string(db_config[source_stage]['user'])
source_pass = _mysql.escape_string(db_config[source_stage]['password'])


# mysqldump the source

print "Running a mysqldump on the source (" + source_stage + ") database..."

sdump = Popen(['ssh', '-p', ssh_ports[source_stage], '-l', users[source_stage], ips[source_stage], 'mysqldump -u ' + source_user + ' -p' + source_pass + ' ' + source_db], stdout=PIPE, stderr=STDOUT, universal_newlines=True)

source_dump = sdump.communicate()


print "Done."
print


# get confirmation from the user
confirm = raw_input("This is your final stop before the push of the database to '" + dest_stage + "'. Once started, it must not be interrupted, or a restore may be needed. Do you want to go ahead? (y/n): ")

if not confirm == 'y' and not confirm == 'Y':
        print "Exiting as requesting."
        exit(1)


print "Pushing the source (" + source_stage + ") database up to " + dest_stage + "..."
print
print "Depending on upload speed and DB size, this may take a few minutes. Please be patient."

# execute against the destination
dest_db = _mysql.escape_string(db_config[dest_stage]['name'])
dest_user = _mysql.escape_string(db_config[dest_stage]['user'])
dest_pass = _mysql.escape_string(db_config[dest_stage]['password'])

dexec = Popen(['ssh', '-p', ssh_ports[dest_stage], '-l', users[dest_stage], ips[dest_stage], 'mysql -u ' + dest_user + ' -p' + dest_pass + ' ' + dest_db], stdin=PIPE, stdout=PIPE, stderr=STDOUT, universal_newlines=True)

dest_result = dexec.communicate(input=source_dump[0])


print "Done."
print

# now, change the variables that need changing
print "Updating the post_content static content URLs on " + dest_stage + "..."

# get the variables ready
old_upload_url_path = _mysql.escape_string(upload_url_paths[source_stage])
new_upload_url_path = _mysql.escape_string(upload_url_paths[dest_stage])
old_upload_path = _mysql.escape_string(upload_paths[source_stage])
new_upload_path = _mysql.escape_string(upload_paths[dest_stage])
old_siteurl = _mysql.escape_string(siteurls[source_stage])
new_siteurl = _mysql.escape_string(siteurls[dest_stage])
old_home = _mysql.escape_string(homes[source_stage])
new_home = _mysql.escape_string(homes[dest_stage])
tblprefix = _mysql.escape_string(tbl_prefix)

# sub into the MySQL commands
sql = "UPDATE `" + tblprefix + "posts` SET post_content = REPLACE(post_content, '" + old_upload_url_path + "', '" + new_upload_url_path + "');\n\
UPDATE `" + tblprefix + "options` SET option_value = '" + new_siteurl + "' WHERE option_name = 'siteurl';\n\
UPDATE `" + tblprefix + "options` SET option_value = '" + new_home + "' WHERE option_name = 'home';\n\
UPDATE `" + tblprefix + "options` SET option_value = '" + new_upload_path + "' WHERE option_name = 'upload_path';\n\
UPDATE `" + tblprefix + "options` SET option_value = '" + new_upload_url_path + "' WHERE option_name = 'upload_url_path';\n\
"

uexec =  Popen(['ssh', '-p', ssh_ports[dest_stage], '-l', users[dest_stage], ips[dest_stage], 'mysql -u ' + dest_user + ' -p' + dest_pass + ' ' + dest_db], stdin=PIPE, stdout=PIPE, stderr=STDOUT, universal_newlines=True)

update_result = uexec.communicate(input=sql)

print "Done."
print


print
print "All done!"
