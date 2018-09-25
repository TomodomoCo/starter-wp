<?php

namespace Tomodomo\Theme;

use Tomodomo\Helpers\Twig;
use Timber;

// Add the Timber context to our container
$app->container['context'] = function ($container) {
    $context = Timber::get_context();

    return $context;
};

$app->container['user'] = function ($container) {
    return $container['context']['user'] ?? null;
};

$app->container['twig'] = function ($container) {
    // Cheating a bit, wrapping Timber
    return new Twig($container);
};
