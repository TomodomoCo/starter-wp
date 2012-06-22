# Require some gems
require "rgbapng"
require "yaml"
project  = YAML.load_file("./config/project.yml")

# Path to theme from project root
project_path      = "./public/content/themes/" + project['application']['theme'] + "/"

# Where's stuff being stored?
css_dir           = "css"
sass_dir          = "sass"
images_dir        = "img"
javascripts_dir   = "js"
fonts_dir         = "fonts"

# Are we in development or production?
environment       = "development"

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