# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant::Config.run do |config|

  ##
  # Set up wpframe
  ##
  require "vpmframe/erb-render"
  require "yaml"
  require "erb"

  project  = YAML.load_file("./config/project.yml")
  database = YAML.load_file("./config/database.yml")

  app_stage        = "dev"
  app_theme        = project['theme']
  app_name         = project['name']
  app_user         = project['user']
  app_group        = project['group']
  site_domain      = project['domain']
  app_domain       = "#{app_stage}." + project['domain']
  app_deploy_to    = "/home/#{app_user}/#{app_domain}"
  app_access_users = project['access_users']

  db_name          = database[app_stage]['name']
  db_user          = database[app_stage]['user']
  db_password      = database[app_stage]['password']
  db_host          = database[app_stage]['host']
  db_grant_to      = database[app_stage]['grant_to']

  ##
  # Set up Vagrant
  ##
  config.vm.box = "vpm_vagrant"
  config.vm.forward_port 80, project['stage'][app_stage]['http_port']
  config.vm.forward_port 22, project['stage'][app_stage]['ssh_port']

  ##
  # Share the path to config files with the VM
  ##
  config.vm.share_folder("config", "/home/deploy/tmp/#{app_name}/#{app_stage}", "./config")

  ##
  # Swap us to set permissions correctly
  ##
  #config.vm.share_folder("v-root", "#{app_deploy_to}/current", ".")
  config.vm.share_folder("v-root", "#{app_deploy_to}/current", ".", :owner => "#{app_user}")

  ##
  # Start your provisioners!
  ##
  config.vm.provision :puppet do |puppet|
    # Grab the manifest erb
    pp_erb = ERB.new( File.read('config/puppet/site.pp.erb') )

    # Write it out to a file
    File.open('config/puppet/rendered/site.pp', 'w') do |f|
      f.write pp_erb.result(binding)
    end

    puppet.manifests_path = "./config/puppet/rendered"
    puppet.manifest_file  = "site.pp"
  end
end
