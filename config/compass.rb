# Require some gems
require 'rgbapng'
require 'sass-globbing'

# Path to theme from project root
project_path      = "./"

# Asset directories
css_dir           = "public/assets/css"
images_dir        = "public/assets/img"
javascripts_dir   = "public/assets/js"
fonts_dir         = "public/assets/fonts"

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
