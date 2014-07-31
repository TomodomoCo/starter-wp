## vpmframe-wp

**vpmframe-wp** is Van Patten Media Inc.'s opinionated framework for developing and deploying new WordPress websites.

It uses **Puppet**, **Capistrano**, **Vagrant**, and a number of other technologies for front-end scaffolding.

We hope this provides a good starting point for others looking to set up a similar development process (Vagrant -> Staging -> Production with Nginx, PHP-FPM, and Varnish). The goal is for a stable, infrequently changing base for WordPress development. Forgive our lack of regular updates... or instead, consider that a feature.

Thanks for your support!

[Chris Van Patten](https://github.com/chrisvanpatten) and [Peter Upfold](https://github.com/PeterUpfold)<br>
(The [Van Patten Media](https://www.vanpattenmedia.com/) Team)

- - -

### Instructions

Detailed instructions coming soon. In the meantime, you'll want to remember `bundle install`, `vagrant up`, `vagrant reload`, `bundle exec guard`, and `bundle exec cap`.

Customise (and, where appropriate, remove the `.example` from) these files:
+ assets.yml
+ database.yml
+ project.yml
+ s3.yml
+ Makefile

Add your theme in `public/content/themes/`.

Be sure to install [image_optim's dependencies](https://github.com/toy/image_optim).

- - -

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

- - -

### License

**Copyright (c) 2012-2014, [Van Patten Media](http://www.vanpattenmedia.com/).**

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

*   Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
*   Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
*   Neither the name of the organization nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

### License Exceptions

Consider any bundled libraries and submodules exceptions to the above. They have their own licenses, which you should follow as appropriate and necessary.
