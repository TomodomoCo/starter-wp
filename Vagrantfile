# -*- mode: ruby -*-
# vi: set ft=ruby :

##
# Handle required plugins
##
[
  "vagrant-exec",
  "vagrant-vbguest",
].each do |plugin|
  need_restart = false

  unless Vagrant.has_plugin? plugin
    system "vagrant plugin install #{plugin}"
    need_restart = true
  end

  exec "vagrant #{ARGV.join(' ')}" if need_restart
end

##
# Do the Vagrant config
##
Vagrant.configure("2") do |config|

  ##
  # Set up vpmframe-wp
  ##
  require "yaml"
  require "erb"

  ##
  # Load our YAML configuration
  ##
  project  = YAML.load_file("./config/project.yml")
  database = YAML.load_file("./config/credentials/database.yml")

  ##
  # Set up initial variables
  ##
  app_stage        = "dev"
  app_name         = project['name']
  app_user         = project['user']
  app_access_users = project['access_users']
  app_group        = project['group']
  app_restrict     = project['stage'][app_stage]['restrict'] ||= false
  app_uploads_dir  = project['uploads_dir'] ||= false
  site_domain      = project['domain']

  # Alternate between different dev URL formats for HTTPS compatibility
  dotcount = project['domain'].scan(/\./).count

  if ( dotcount === 2 )
    app_domain = "#{app_stage}-" + project['domain']
  else
    app_domain = "#{app_stage}." + project['domain']
  end

  # Set app base
  app_deploy_to = "/home/#{app_user}/#{app_domain}"

  # Set DB information
  db_name     = database[app_stage]['name']
  db_user     = database[app_stage]['user']
  db_password = database[app_stage]['password']
  db_host     = database[app_stage]['host']
  db_grant_to = database[app_stage]['grant_to']

  # Set up Vagrant box
  config.vm.box = "vpm_vagrant_jessie_2015-08"

  # Use a private network with the IP pulled from project.yml
  config.vm.network "private_network", ip: project['stage'][app_stage]['ip']

  # Share the path to config files with the VM
  config.vm.synced_folder "./config", "/home/deploy/tmp/#{app_name}/#{app_stage}"

  # Handle creating the synced folder.
  # (Note: using a manual UID for a user that will be created during provisioning)
  config.vm.synced_folder ".", "#{app_deploy_to}/current", :owner => 9999

  # Make sure `vagrant exec` commands are issued from the right folder
  config.exec.commands "*", directory: "#{app_deploy_to}/current"

  ##
  # Special VirtualBox configuration settings
  ##
  config.vm.provider "virtualbox" do |v|
    # Enable linked clones
    v.linked_clone = true if Vagrant::VERSION =~ /^1.8/
  end

  ##
  # Start your provisioners!
  ##
  config.vm.provision "puppet" do |puppet|
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
