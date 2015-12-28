##
# Set stage
##
set :app_stage, "staging"

##
# Load configuration YML
##
set :project_yml_path,  "./config/project.yml"
set :database_yml_path, "./config/database.yml"
project  = YAML.load_file(fetch(:project_yml_path))
database = YAML.load_file(fetch(:database_yml_path))

##
# Stage-specific server options
##
set :app_server, project['stage'][fetch(:app_stage)]['ip']
set :app_port,   project['stage'][fetch(:app_stage)]['ports']['ssh']

server fetch(:app_server), :app, :web, :db, :primary => true
ssh_options[:port] = fetch(:app_port)

##
# Stage-specific application info
##

# Alternate between different dev URL formats for HTTPS compatibility
dotcount = project['domain'].scan(/\./).count

if ( dotcount === 2 )
  set :app_domain, "#{app_stage}-" + project['domain']
else
  set :app_domain, "#{app_stage}." + project['domain']
end

set :deploy_to,     "/home/#{fetch(:app_user)}/#{fetch(:app_domain)}"
set :app_deploy_to, fetch(:deploy_to)
set :branch,        project['stage'][fetch(:app_stage)]['branch']

##
# Database info
##
set :db_name,     database[fetch(:app_stage)]['name']
set :db_user,     database[fetch(:app_stage)]['user']
set :db_password, database[fetch(:app_stage)]['password']
set :db_host,     database[fetch(:app_stage)]['host']
set :db_grant_to, database[fetch(:app_stage)]['grant_to']
