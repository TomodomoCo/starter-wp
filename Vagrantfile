# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant::Config.run do |config|
  config.vm.box = "vpm_vagrant"

  if File.exist?("./config/vagrant-custom.rb")
    require "./config/vagrant-custom.rb"
  else
    config.vm.forward_port 80, 8080
  end

  # Basic requirements
  require "vpmframe/erb-render"
  require "yaml"
  require "erb"

  project  = YAML.load_file("./config/project.yml")
  database = YAML.load_file("./config/database.yml")

  app_theme        = project['application']['theme']
  app_name         = project['application']['name']
  app_user         = project['application']['user']
  app_group        = project['application']['group']
  app_stage        = "dev"
  site_domain      = project['application']['domain']
  app_domain       = "#{app_stage}." + project['application']['domain']
  app_deploy_to    = "/home/#{app_user}/#{app_domain}"
  app_access_users = project['application']['access_users']

  db_name          = database['dev']['name']
  db_user          = database['dev']['user']
  db_password      = database['dev']['password']
  db_host          = database['dev']['host']
  db_grant_to      = database['dev']['grant_to']

  config.vm.share_folder("config", "/home/deploy/tmp/#{app_name}/#{app_stage}", "./config")
  config.vm.share_folder("v-root", "#{app_deploy_to}/current", ".")
#  config.vm.share_folder("v-root", "#{app_deploy_to}/current", ".", :owner => "#{app_user}")

  config.vm.provision :puppet do |puppet|
    # Grab the manifest erb
    pp_erb = ERB.new( File.read('config/puppet/site.pp.erb') )

    # Write it out to a file
    File.open('config/puppet/rendered/site.pp', 'w') do |f|
      f.write pp_erb.result(binding)
    end

    puppet.manifests_path = "./config/puppet/rendered"
    puppet.manifest_file = "site.pp"
  end
end