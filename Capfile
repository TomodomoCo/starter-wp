# Load DSL and set up stages
require "capistrano/setup"

# Include default deployment tasks
require "capistrano/deploy"

# Include git support
require "capistrano/scm/git"
install_plugin Capistrano::SCM::Git

# Include external tasks
require "capistrano/composer"
require "capistrano/copy_files"
require "capistrano/vpmframe"

# Load custom tasks from `lib/capistrano/tasks` if you have any defined
Dir.glob("lib/capistrano/tasks/*.rake").each { |r| import r }
