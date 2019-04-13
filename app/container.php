<?php

namespace Tomodomo\Theme;

use Tomodomo\Helpers\Twig;
use Timber;

// Add the Timber context to our container
$app->container['context'] = function ($container) {
    $context = Timber::get_context();

    return $context;
};

// Allow accessing the current user
$app->container['user'] = function ($container) {
    return $container['context']['user'] ?? null;
};

// Add an instance of Twig
$app->container['twig'] = function ($container) {
    return new Twig($container);
};
