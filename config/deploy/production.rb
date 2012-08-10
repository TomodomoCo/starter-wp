# Set stage
set :app_stage, "production"

project  = YAML.load_file("./config/project.yml")
database = YAML.load_file("./config/database.yml")


# Server options
server project['application']['servers'][fetch(:app_stage)]['ip'], :app, :web, :db, :primary => true
ssh_options[:port]          = project['application']['servers'][fetch(:app_stage)]['port']
default_run_options[:pty]   = true
ssh_options[:forward_agent] = true

# Pull in DB config
set :db_name,     database[fetch(:app_stage)]['name']
set :db_user,     database[fetch(:app_stage)]['user']
set :db_password, database[fetch(:app_stage)]['password']
set :db_host,     database[fetch(:app_stage)]['host']
set :db_grant_to, database[fetch(:app_stage)]['grant_to']

# nginx config
set :app_name,    project['application']['name']
set :app_theme,   project['application']['theme']
set :site_domain, project['application']['domain']
set :app_domain,  project['application']['domain']

# Deploy path
set :deploy_to,     "/home/#{fetch(:app_user)}/#{fetch(:app_domain)}"
set :app_deploy_to, fetch(:deploy_to)
