# Load configuration YML
set :project_yml_path, "./config/project.yml"
project  = YAML.load_file(fetch(:project_yml_path))

set :app_target, "#{project['stage']['production']['ip']}"
set :app_user, "#{project['stage']['production']['user']}"
set :app_port, "#{project['stage']['production']['ports']['ssh']}"

# Server settings
server "#{fetch(:app_target)}",
  roles: [:app],
  user: "#{fetch(:app_user)}",
  port: "#{fetch(:app_port)}"

# Stage settings
set :app_domain, "#{project['stage']['production']['domain']}"
set :branch,     "#{project['stage']['production']['branch']}"
set :tmp_dir,    "#{project['stage']['production']['deploy_to']}/.tmp"
set :deploy_to,  "#{project['stage']['production']['deploy_to']}"
