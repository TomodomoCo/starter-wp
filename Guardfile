require "yaml"
project = YAML.load_file("./config/project.yml")

group :development do
  guard 'compass' do
    watch(%r{(.*)\.s[ac]ss$})
  end

  guard 'livereload' do
    watch(%r{.+\.(css|js|html?|php|inc|png|jpg|gif)$})
  end

  guard 'jammit', :output_folder => "./public/content/themes/" + project["application"]["theme"] + "/js/" do
    watch('config/assets.yml') # Make sure we're using the latest assets.yml file
    watch(%r{(?:javascripts)(/.+)\.(js)}) { |m| m[0] unless m[1] =~ /\/\./ }
  end
end