# Set stage
set :app_stage, "staging"

set :project_yml_path,  "./config/project.yml"
set :database_yml_path, "./config/database.yml"

project = YAML.load_file(fetch(:project_yml_path))

# Server options
server project['application']['servers'][fetch(:app_stage)]['ip'], :app, :web, :db, :primary => true
ssh_options[:port]          = project['application']['servers'][fetch(:app_stage)]['port']
default_run_options[:pty]   = true
ssh_options[:forward_agent] = true

set :application, project["application"]["name"]
set :app_domain,  "#{app_stage}." + project['application']['domain']

require 'vpmframe/capistrano/base'
require 'vpmframe/capistrano/database'
require 'vpmframe/capistrano/multistage'