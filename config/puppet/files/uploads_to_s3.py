#!/usr/bin/env python
#
#
# Push WordPress uploads to Amazon S3
#
# This script pushes temporary content in uploads.<%= app_domain %> up
# to Amazon S3 on a regular basis, and clears out our temporary copies.
#
#
# Requires python-boto and PyYAML

import yaml
from sys import exit
import sys
import os
from os.path import relpath, exists
import boto
from boto.s3.connection import S3Connection
from boto.s3.bucket import Bucket
from boto.s3.key import Key


# check arguments
if len(sys.argv) < 3:
        print "Usage: " + os.path.basename(__file__) + " config_path content_directory"
        exit(1)


# bring in config path and content directory from CLI
config_path = sys.argv[1]
content_directory = sys.argv[2]

# sanity checking for directories
if not exists(config_path) or not exists(content_directory):
	print "Could not open config path or content directory. Do they both exist?"
	exit(1)

# bring in S3 credentials from YAML
try:
	config_file = open(config_path, 'r')
except IOError as e:

	print "Could not open S3 configuration file from the config path."
	print "I/O Error({0}): {1}".format(e.errno, e.strerror)
	print "Cannot continue."
	exit(1)

try:
	config = yaml.safe_load(config_file)
except yaml.YAMLError as e:
	print "Unable to parse S3 configuration file."
	print "YAMLError({0}): {1}".format(e.errno, e.strerror)

# sanity checking of config YAML
if not 'bucket_name' in config:
	print "The bucket_name was not specified in the S3 config YAML file."
	exit(1)
if not 'access_key' in config:
	print "The access_key was not specified in the S3 config YAML file."
	exit(1)
if not 'secret_access_key' in config:
	print "The secret_access_key was not specified in the S3 config YAML file."
	exit(1)

try:
	# connect to S3
	s3 = S3Connection(config['access_key'], config['secret_access_key'])

	# connect to the bucket
	bucket = Bucket(s3, config['bucket_name'])
except S3ResponseError as e:
	print "Unable to connect to S3."
	print "S3ResponseError({0}): {1}.".format(e.errno, e.strerror)
	exit(1)


# loop through uploads. directory
for root, dirs, files in os.walk(content_directory):
	for file in files:

		# get full directory path (e.g. /home/         /uploads.../content/uploads/
		#								2012/06/test.jpg)
		this_file = os.path.join(root, file)

		# get relative path for URI (e.g. content/uploads/2012/06/test.jpg)
		this_file_relative = relpath(this_file, content_directory)

		print "file = " + this_file
		print "relative = " + this_file_relative
		print

		# is this file on S3?
		this_key = bucket.get_key(this_file_relative)

		if not this_key:
			# upload to S3

			print this_file_relative + " is not on S3. Uploading..."

			# create a new key in the bucket
			this_key = bucket.new_key(this_file_relative)

			# upload our file as this key's contents
			try:
				this_key.set_contents_from_filename(this_file, None, True)

				this_key.set_acl('public-read')

			except S3ResponseError as e:
					print "Unable to upload "  + this_file_relative + " to Amazon S3."
					print "S3ResponseError({0}): {1}.".format(e.errno, e.strerror)

			# is the file now there?
			this_key = bucket.get_key(this_file_relative)

			if this_key:
				# delete our copy
				os.remove(this_file)
			else:
				print "The upload of " + this_file_relative + " did not seem to succeed."
		print
		print
