##
# Load the project information
##
set :project_yml_path, "./config/project.yml"
project = YAML.load_file(fetch(:project_yml_path))

# Require multistage for local->staging->production deployment...
require 'capistrano/ext/multistage'

# Require tmpdir for local asset compilation
require 'tmpdir'

##
# Deploy settings
##
set :scm,                     :git
set :git_enable_submodules,   1
set :stages,                  ["staging", "production"]
set :default_stage,           "staging"
default_run_options[:pty]   = true
ssh_options[:forward_agent] = true

##
# Set project/app variables
##
set :application,      project['name']
set :app_name,         project['name']
set :user,             project['deploy_user']
set :app_user,         project['user']
set :app_group,        project['group']
set :app_access_users, project['access_users']
set :app_uploads_dir,  project['uploads_dir']
set :repository,       project['repo']
set :site_domain,      project['domain']
set :tmpdir,           Dir.mktmpdir

##
# Set alerting variables
##
set :alerts_slack_room, project['alerts']['slack']['room']
set :alerts_slack_hook, project['alerts']['slack']['hook']

##
# Load vpmframe requirements
##
require 'vpmframe/capistrano/assets'
require 'vpmframe/capistrano/composer'
require 'vpmframe/capistrano/puppet'
require 'vpmframe/capistrano/credentials'
require 'vpmframe/capistrano/permissions'
require 'vpmframe/capistrano/wp-salts'

##
# Override native Capistrano tasks
##
namespace :deploy do
  task :finalize_update do transaction do end end
  task :migrate do end

  desc "Restart nginx"
  task :restart do
    run "#{sudo} nginx -s reload"
  end
end

##
# Setup related tasks
##
before "deploy:setup",
  "puppet:show"

after "deploy:setup",
  "permissions:fix_setup_ownership",
  "salts:generate_wp_salts"

##
# Upload and symlink DB credentials
##
before "deploy:create_symlink",
  "credentials:upload_credentials",
  "credentials:symlink_credentials",
  "salts:symlink_wp_salts"

##
# Compile and upload assets
##
before "deploy",
  "assets:local_temp_clone",
  "assets:compile_local_assets"

before "deploy:create_symlink",
  "assets:upload_local_assets"

##
# Install composer dependencies
##
after "deploy:update_code",
  "composer:install"

before "composer:install",
  "composer:copy_vendors"

##
# Fix ownership
##
before "deploy:restart",
  "permissions:fix_deploy_ownership"

##
# Cleanup
##
after "deploy",
  "deploy:cleanup",
  "assets:local_temp_cleanup",
  "alerts:slack"
