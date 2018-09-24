# Load project configuration
set :project_yml_path, "./config/project.yml"
project = YAML.load_file(fetch(:project_yml_path))

# General settings
set :application,   project['name']
set :repo_url,      project['repo']
set :use_sudo,      false
set :keep_releases, 5

# Directories and such
set :linked_dirs, ['config/secrets', 'vendor/composer', 'public/content/uploads']
set :copy_files,  ['public/.htaccess', 'public/.well-known', 'config/wp-salts.php']
set :build_dir,   Dir.mktmpdir
set :uploads,     project['uploads']

# Composer settings
set :composer_install_flags, '--no-interaction --optimize-autoloader'
SSHKit.config.command_map[:composer] = "composer"

# Slack notification
set :slack, {
  channel: "#{project['alerts']['slack']['channel']}",
  webhook: "#{project['alerts']['slack']['webhook']}"
}

# Override restart tasks
namespace :deploy do
  after :restart, :clear_cache do
    on roles(:app), in: :groups, limit: 3, wait: 10 do
      # This space left intentionally blank
    end
  end
end

# Hook our tasks
after 'deploy:updated', 'build:clone'
after 'deploy:updated', 'build:build'
after 'deploy:updated', 'build:upload'
after 'deploy:updated', 'build:clean'
after 'deploy:updated', 'credentials:salts'
after 'deploy:finished', 'alerts:slack'
