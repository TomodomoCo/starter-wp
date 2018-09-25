# Load configuration YML
set :project_yml_path, "./config/project.yml"
project  = YAML.load_file(fetch(:project_yml_path))

set :app_target, "#{project['stage']['staging']['ip']}"
set :app_user, "#{project['stage']['staging']['user']}"
set :app_port, "#{project['stage']['staging']['ports']['ssh']}"

# Server settings
server "#{fetch(:app_target)}",
  roles: [:app],
  user: "#{fetch(:app_user)}",
  port: "#{fetch(:app_port)}"

# Stage settings
set :app_domain, "#{project['stage']['staging']['domain']}"
set :branch,     "#{project['stage']['staging']['branch']}"
set :tmp_dir,    "#{project['stage']['staging']['deploy_to']}/.tmp"
set :deploy_to,  "#{project['stage']['staging']['deploy_to']}"
