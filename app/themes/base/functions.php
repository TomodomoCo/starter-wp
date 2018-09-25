<?php

namespace Tomodomo\Theme;

use Tomodomo\Models\Menu;

/**
 * Add theme support
 *
 * @return void
 */
function themeSupports()
{
    // Featured images
    add_theme_support('post-thumbnails');

    // Gutenberg wide alignment
    add_theme_support('align-wide');

    // Disable Gutenberg colors
    add_theme_support('disable-custom-colors');

    // Auto-generate the title tag
    add_theme_support('title-tag');

    return;
}

add_action('after_setup_theme', __NAMESPACE__ . '\\themeSupports');

/**
 * Register theme nav menus
 *
 * @return void
 */
function registerMenus()
{
    register_nav_menus([
        'primary' => 'Primary Menu',
        'footer'  => 'Footer Menu',
    ]);

    return;
}

add_action('init', __NAMESPACE__ . '\\registerMenus');

/**
 * Add items to Timber context to access on views
 *
 * @param array $context
 *
 * @return array
 */
function context($context)
{
    // Load in menus
    $context['menu']['primary'] = new Menu('primary');
    $context['menu']['footer']  = new Menu('footer');

    return $context;
}

add_filter('timber/context', __NAMESPACE__ . '\\context');
