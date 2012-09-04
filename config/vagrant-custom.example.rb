Vagrant::Config.run do |config|
  config.vm.forward_port 80, XXXX
  config.vm.forward_port 22, XXXX
end