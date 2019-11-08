<?php

namespace Tomodomo;

use Tomodomo\Kaiso as App;
use Timber as Timber;

// Instantiate Timber
$timber = new Timber\Timber();

// Define our view location
/**
 * @psalm-suppress UndefinedConstant
 * @psalm-suppress UndefinedClass
 */
Timber::$locations = [
    ABSPATH . '/../../app/views',
];

// Instantiate the app with our settings
require_once ABSPATH . '/../../app/settings.php';

$app = new App($settings);

// Load up the container
require_once ABSPATH . '/../../app/container.php';

// Run the app!
$app->run();
