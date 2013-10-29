require "yaml"
project = YAML.load_file("./config/project.yml")

group :development do

  guard 'livereload' do
    watch(%r{.+\.(css|js|html?|php|inc|png|jpg|gif)$})
  end

  guard 'shell' do

    # images
    watch(%r{app/assets/images/(.+\/)?(.+\.[gif|jpg|png]+)}) do |m|
      `mkdir -p ./public/content/themes/#{project["theme"]}/img/#{m[1]}`
      `cp #{m[0]} ./public/content/themes/#{project["theme"]}/img/#{m[1]}#{m[2]}`
      `image_optim --no-pngout ./public/content/themes/#{project["theme"]}/img/#{m[1]}#{m[2]}`
    end

    # css
    watch(%r{(.*)\.s[ac]ss$}) do
      `make css`
    end

    # javascripts
    watch(%r{(?:javascripts)(/.+)\.(js)}) do
      `make javascripts`
    end

    watch('config/assets.yml') do
      `make javascripts`
    end

  end

end
