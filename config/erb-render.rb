# -*- mode: ruby -*-
# vi: set ft=ruby :

# Defines a function, render(), that we use to include one 
# ERB fragment from another.
#
# This is used both by the Vagrantfile and by Capistrano's
# deploy.rb.
#
#

require "erb"

def render path
  content = File.read(File.expand_path(path))
  t = ERB.new(content)
  t.result(binding)
end
