<?php
/**
 * Kaiso brings a number of modern PHP best practices to WordPress,
 * but also brings along some core WordPress functionality —
 * including a functions.php file, which can run functionality
 * automatically in your site.
 *
 * While you can put any code here, we recommend using this file to
 * configure "environment" settings: defining theme supports,
 * registering nav menus, adding to Timber's global context, etc.
 */

namespace Tomodomo\Theme;

use Tomodomo\Models\Menu;

/**
 * Add theme support
 *
 * @return void
 */
function themeSupports() : void
{
    // Featured images
    add_theme_support('post-thumbnails');

    // Gutenberg wide alignment
    add_theme_support('align-wide');

    // Disable Gutenberg colors
    add_theme_support('disable-custom-colors');

    // Disable Gutenberg custom font sizes
    add_theme_support('disable-custom-font-sizes');

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
function registerMenus() : void
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
function context(array $context) : array
{
    // Load in menus
    $context['menu']['primary'] = new Menu('primary');
    $context['menu']['footer']  = new Menu('footer');

    return $context;
}

add_filter('timber/context', __NAMESPACE__ . '\\context');
