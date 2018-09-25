<?php

namespace Tomodomo\Theme;

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

// App settings. So far you only need to provide a controllerPath
$settings = [
    'controllerPath'  => '\\Tomodomo\\Controllers\\',
    'customTemplates' => [],
];

// Instantiate the app with our settings
$app = new App($settings);

// Load up the container
require_once 'container.php';

// Run the app!
$app->run();
