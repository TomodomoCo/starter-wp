# Require some gems
require 'rgbapng'
require 'sass-globbing'

# Load project config
require 'yaml'
project  = YAML.load_file("./config/project.yml")

# Path to theme from project root
project_path      = "./"

# Where's stuff being spit out?
css_dir           = "public/content/themes/" + project['theme'] + "/css"
images_dir        = "public/content/themes/" + project['theme'] + "/img"
javascripts_dir   = "public/content/themes/" + project['theme'] + "/js"
fonts_dir         = "public/content/themes/" + project['theme'] + "/fonts"

# Where are we pulling from?
sass_dir          = "app/assets/sass"
add_import_path   = "vendor/sass"

# Are we in development or production?
environment       = "production"

# What should environments look like?
if environment == "production"
  output_style  = :compressed
  line_comments = false
else
  output_style  = :expanded
  line_comments = true
end

# Enable relative asset paths
relative_assets = true
