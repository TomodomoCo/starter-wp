# Require multistage for local->staging->production deployment...
require 'capistrano/ext/multistage'

# Load the project information
set :project_yml_path, "./config/project.yml"

# Load vpmframe requirements
require 'vpmframe/erb-render'
require 'vpmframe/capistrano/base'
require 'vpmframe/capistrano/assets'
require 'vpmframe/capistrano/puppet'
require 'vpmframe/capistrano/credentials'
require 'vpmframe/capistrano/permissions'

# Don't do Railsy things...
namespace :deploy do
  task :finalize_update do transaction do end end
  task :migrate do end

  desc "Restart nginx"
  task :restart do
    run "#{sudo} nginx -s reload"
  end
end

# Setup related tasks
before "deploy:setup", "puppet:show"
after "deploy:setup", "permissions:fix_setup_ownership"

# Upload and symlink DB credentials
before "deploy:create_symlink", "credentials:upload_db_cred", "credentials:symlink_db_cred"

# Compile and upload assets
before "deploy", "assets:local_temp_clone"
before "deploy:create_symlink", "assets:upload_asset_css", "assets:upload_asset_js", "assets:upload_asset_images"

# Fix ownership
before "deploy:restart", "permissions:fix_deploy_ownership"

# Cleanup
after "deploy", "deploy:cleanup", "assets:local_temp_cleanup"