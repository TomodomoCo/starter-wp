# Load the project information
set :project_yml_path, "./config/project.yml"
project = YAML.load_file(fetch(:project_yml_path))

# Require multistage for local->staging->production deployment...
require 'capistrano/ext/multistage'

# Require tmpdir for local asset compilation
require 'tmpdir'

set :scm,                     :git
set :git_enable_submodules,   1
set :stages,                  ["staging", "production"]
set :default_stage,           "staging"
default_run_options[:pty]   = true
ssh_options[:forward_agent] = true
set :use_sudo, false
default_run_options[:shell] = '/bin/bash -l'

set :application,      project['name']
set :app_name,         project['name']
set :user,             project['deploy_user']
set :app_user,         project['user']
set :app_group,        project['group']
set :app_access_users, project['access_users']
set :app_theme,        project['theme']
set :repository,       project['repo']
set :site_domain,      project['domain']
set :tmpdir,           Dir.mktmpdir

# Set alerting variables
set :alerts_hipchat_room, project['alerts']['hipchat']['room']
set :alerts_hipchat_key,  project['alerts']['hipchat']['key']

# Load vpmframe requirements
require 'vpmframe/erb-render'
require 'vpmframe/capistrano/alerts'
require 'vpmframe/capistrano/assets'
require 'vpmframe/capistrano/composer'
require 'vpmframe/capistrano/puppet'
require 'vpmframe/capistrano/credentials'
require 'vpmframe/capistrano/permissions'
require 'vpmframe/capistrano/wp-salts'

# Don't do Railsy things...
namespace :deploy do
  task :finalize_update do transaction do end end
  task :migrate do end

  desc "Restart nginx"
  task :restart do
  end
end

namespace :wordpress do
  desc "Copy .htaccess file from previous release"
  task :copy_htaccess, :except => { :no_release => true } do
    run "if [ -f #{previous_release}/public/.htaccess ]; then cp -a #{previous_release}/public/.htaccess #{latest_release}/public/.htaccess; fi"
  end
end

# Generate salts
after "deploy:setup",
  "salts:generate_wp_salts"

# Upload and symlink DB credentials
before "deploy:create_symlink",
  "credentials:upload_db_cred",
  "credentials:symlink_db_cred",
  "salts:symlink_wp_salts"

# Compile and upload assets
before "deploy",
  "assets:local_temp_clone",
  "assets:compile_local_assets"

before "deploy:create_symlink",
  "assets:upload_local_assets",
  "wordpress:copy_htaccess"

# Install composer dependencies
after "deploy:update_code",
  "composer:install"

before "composer:install",
  "composer:copy_vendors"

# Cleanup
after "deploy",
  "deploy:cleanup",
  "assets:local_temp_cleanup",
  "alerts:hipchat"
