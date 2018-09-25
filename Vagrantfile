# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  # Ruby dependencies
  require "yaml"

  # YAML config
  project  = YAML.load_file("./config/project.yml")
  database = YAML.load_file("./config/secrets/database.yml")

  # Network
  config.vm.box = "ubuntu/trusty64"

  # Do some network configuration
  config.vm.network "private_network", ip: project['stage']['dev']['ip']

  # Mount shared folder using NFS
  config.vm.synced_folder ".", "/home/vagrant/#{project['stage']['dev']['domain']}/current"

  # VirtualBox config
  config.vm.provider :virtualbox do |v|
	# Give our box enough memory
	v.memory = 1024

    # Linked clone support
    v.linked_clone = true if Vagrant::VERSION =~ /^1.8/
  end

  # Assign hostname
  config.vm.hostname = project['stage']['dev']['domain']

  # Provision the box
  config.vm.provision :shell,
    :path => "config/vagrant/bootstrap.sh",
    :env  => {
      "DB_NAME"    => database['dev']['name'],
      "APP_DOMAIN" => project['stage']['dev']['domain'],
    }
end
