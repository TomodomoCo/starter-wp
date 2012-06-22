## wpframe from Van Patten Media

This is our highly-opinionated framework for developing and deploying new WordPress websites.

It uses the following technologies:

*   Puppet
*   Capistrano
*   Vagrant
*   Compass
*   And a whole lotta Git and YAML (via Symfony YAML)

It assumes a lot about the set up of your development process and servers. For example...

*   We use...
    *   Puppet for provisioning (local and remotes)
    *   Nginx and PHP-FPM for serving sites
    *   Varnish for caching
    *   A "remote" database server on a local network, connected via SSL and a custom wpdb class
*   We have a "deploy" user that actually executes deployments
*   Our development process is three stages (local/staging/production) with local dev happening in the Vagrant box
*   Vagrant is set up for host-only networking

It's not perfect, but it works for us. To use it for your own server, you'll probably need to make modifications. You'll definitely need to bring your own Vagrant box, and probably have to flesh out the Puppet manifests as a result to get things in order. It's not for the faint-of-heart, but we've provided a good structure to start with.

We hope this provides a good starting point for others looking to set up a similar development process (Vagrant -> Staging -> Production with Nginx, PHP-FPM, and Varnish). We probably won't be developing this heavily, although we will certainly give consideration to any pull requests and answer any questions we receive.

Thanks!

[Chris Van Patten](https://github.com/chrisvanpatten) and [Peter Upfold](https://github.com/PeterUpfold)<br>
(The [Van Patten Media](http://www.vanpattenmedia.com/) Team)

### Getting started

There are a few things you'll need to do to get started.

1.  Install [Vagrant](http://downloads.vagrantup.com/).
2.  Run `git clone git://github.com/vanpattenmedia/wpframe.git projectname && cd projectname && rm -rf .git` to prepare your project directory
3.  Run `gem install bundler` to install [Bundler](http://gembundler.com/), then `bundle install` to install the required Ruby dependencies
4.  Edit the [Vagrantfile](https://github.com/vanpattenmedia/wpframe/blob/master/Vagrantfile) to use your own [box](https://github.com/vanpattenmedia/wpframe/blob/master/Vagrantfile#L5). There are some available at [VagrantBox.es](http://www.vagrantbox.es/).
5.  `git init && git commit -am 'Initial commit'` - get this puppy in version control again.
6.  `mv config/project.example.yml config/project.yml` and edit the result to use your project's info (you may not have a repo yet; that's okay, you don't need it until you deploy to a remote)
7.  `mv config/database.example.yml config/database.yml` and add in some new DB credentials. Keep in mind these are **new** credentials - Puppet will generate new databases and users based on what you set here. The databases _should not exist_.
8.  Edit your hosts file to point `dev.yourdomain.com` to the IP set in the Vagrantfile
9.  `vagrant up` - launch Vagrant!
10.  Visit [http://dev.yourdomain.com/wp/] to complete WordPress setup. You may need to manually edit the database to use the /wp/ as admin convention.

#### Staging and production

1.  Make sure your remote server has SSH key access set up, and that your deploy user has sudo access
2.  Make sure you have a Git repo in place by now.
3.  Run `cap staging deploy:setup`
4.  If everything runs without error, run `cap staging deploy` to execute a deploy
5.  You can reprovision at any time with `cap staging puppet:show`
6.  To setup/deploy/reprovision on production, follow the same steps, but replace "`staging`" with "`production`".

Enjoy!

### Special thanks to

*   [Mark Jaquith](http://markjaquith.com/)
    *   For inspiring bits of this project (and its release) with his [Skeleton Repo](https://github.com/markjaquith/WordPress-Skeleton)
    *   For making sure WordPress has a [Git mirror](github.com/wordpress/wordpress) on Github
*   The various projects we use to make this a reality, including
    *   [Puppet](http://puppetlabs.com/)
    *   [Capistrano](https://github.com/capistrano/capistrano)
    *   [Vagrant](http://vagrantup.com/)
    *   [Symfony YAML](http://symfony.com/doc/current/components/yaml.html)
    *   [WordPress](http://www.wordpress.org/)

### License

**Copyright &copy; 2012, [Van Patten Media](http://www.vanpattenmedia.com/).**

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

*   Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
*   Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
*   Neither the name of the organization nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

### License Exceptions

Consider any bundled libraries and submodules exceptions to the above. They have their own licenses, which you should follow as appropriate and necessary.