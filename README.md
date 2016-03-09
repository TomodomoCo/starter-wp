## vpmframe-wp

**vpmframe-wp** is Van Patten Media Inc.'s opinionated framework for developing and deploying new WordPress websites.

### Instructions

1. Install Vagrant, Ruby (we recommend via RVM), and Node w/ npm
2. Add the Vagrant box
3. Tweak some config files:
    + Rename `config/credentials-example/` to `config/credentials/`
    + `config/project.yml` should contain project-specific settings
    + `config/credentials/database.example.yml` should be renamed to `database.yml` and contain DB settings
    + `config/credentials/s3.example.yml` should be renamed to `s3.yml`, if you intend to use the [S3-Uploads](https://github.com/humanmade/S3-Uploads) plugin (we like it and recommend it)
4. `make install`
5. `vagrant up`

Add your theme in `public/content/themes/` (or `app/views/`, symlinked to the themes folder)

### Changelog

*   **9 March 2015**
    *   We use a `config/credentials/` folder now to store all secure credentials
    *   Update deploy recipes for credentials folder
    *   Bump WP version
    *   Use https repos for Composer
    *   Disable WordPress' emoji replacement by default
*   **28 December 2015**
    *   Basic auth restrictions are now set in project.yml and provisioned by Puppet. If you need to change your auth username/password, you'll need to re-run Puppet.
    *   Creating an uploads directory is optional, via project.yml. No need to edit the Puppet manifest to remove it.
    *   Replaced gulp-minify-css with [gulp-cssnano](https://github.com/ben-eb/gulp-cssnano)
*   **25 December 2015**
    *   Vagrant comment flipping is no longer required; it now uses manually set UIDs to ensure the right user has access
    *   Required plugins are automatically installed before Vagrant brings up a box
    *   Run commands from the working directory within the Vagrant box using `vagrant exec command`
    *   When running a deploy or Puppet show, vpmframe tries to help determine whether your stage subdomains should be in the format `dev.domain.com` or dev-subdomain.domain.com` to help with SSL cert compatibility. This may not work for international TLDs such as .co.uk!
    *   The `erb-render` dependency has been removed
    *   Gulp is now the official asset compilation method of choice. Access it with `npm run gulp`
    *   Bower is supplied by default. Access it with `npm run bower`
    *   JS is now indented with 2 spaces, not a 4-character-length tab
    *   Asset cleaning commands have been moved into Gulp, and the Makefile has been appropriately simplified

### License

**Copyright (c) 2012-2015, [Van Patten Media](http://www.vanpattenmedia.com/).**

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

*   Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
*   Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
*   Neither the name of the organization nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
