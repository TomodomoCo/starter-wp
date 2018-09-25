# starter-wp

A highly opinionated starter framework for WordPress.

Leverages [Kaiso](https://github.com/TomodomoCo/kaiso) and [Timber](https://github.com/timber/timber) for a more modern, concern-separated approach to WordPress development. Installs [psalm](https://github.com/vimeo/psalm) and [phpcs](https://github.com/squizlabs/PHP_CodeSniffer) for linting and static analysis. Uses [gulp](https://github.com/gulpjs/gulp) as a front-end build system.

## Usage

Vagrant setup:

1. `git clone [repo]`
2. `cp -r app/secrets-example app/secrets`
3. Fill out files in `app/secrets/`
4. `vagrant up`

Building the project:

1. `composer install`
2. `nvm install && nvm use`
3. `npm install`
4. `npm run dev` or `npm run build`

Linting:

+ `npm run lint-php` for both `phpcs` and `psalm`
+ `npm run phpcs` or `./vendor/composer/bin/phpcs`
+ `npm run psalm` or `./vendor/composer/bin/psalm`

Building plugin dependencies (e.g. for Gutenberg blocks):

1. `npm run lerna-install`
2. `npm run lerna-dev` or `npm run lerna-build`

## About Tomodomo

Tomodomo is a creative agency for magazine publishers. We use custom design and technology to speed up your editorial workflow, engage your readers, and build sustainable subscription revenue for your business.

Learn more at [tomodomo.co](https://tomodomo.co) or email us: [hello@tomodomo.co](mailto:hello@tomodomo.co)

## License

© 2018 Van Patten Media Inc. d/b/a Tomodomo.

This project is licensed under the terms of the MIT License, included in `LICENSE.md`.

## Code of Conduct

All open source Tomodomo projects follow a strict code of conduct, included in `CODEOFCONDUCT.md`. We ask that all contributors adhere to the standards and guidelines in that document.

Thank you!
