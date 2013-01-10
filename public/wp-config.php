<?php

/**
 * Setup the YAML parser, load some yaml files
 */
require_once( dirname( __FILE__ ) . './../vendor/php/yaml/lib/sfYamlParser.php' );
$yaml     = new sfYamlParser();
$project  = $yaml->parse( file_get_contents( dirname( __FILE__ ) . './../config/project.yml' ) );
$database = $yaml->parse( file_get_contents( dirname( __FILE__ ) . './../config/database.yml' ) );

/**
 * Setup the dev, staging, and production environments
 */
$urlParts = explode( '.', $_SERVER['HTTP_HOST'] );
if ( $urlParts[0] == 'dev' ) {
	/**
	 * DEV
	 */
	define( 'WP_STAGE', $urlParts[0] );
	define( 'WP_HOME', 'http://' . WP_STAGE . '.' . $project['domain'] );

	// Make "private"
	update_option( 'blog_public', 0 );

	// Show errors
	ini_set( 'display_errors', 1 );
	define( 'WP_DEBUG', true );
	define( 'WP_DEBUG_DISPLAY', true );
} elseif ( $urlParts[0] == 'staging' ) {
	/**
	 * STAGING
	 */
	define( 'WP_STAGE', $urlParts[0] );
	define( 'WP_HOME', 'http://' . WP_STAGE . '.' . $project['domain'] );

	// Make "private"
	update_option( 'blog_public', 0 );

	// Hide errors
	ini_set( 'display_errors', 0 );
	define( 'WP_DEBUG', false );
	define( 'WP_DEBUG_DISPLAY', false );
} else {
	/**
	 * PRODUCTION
	 */
	define( 'WP_STAGE', 'production' );
	define( 'WP_HOME', 'http://www.' . $project['domain'] );

	// Make public
	update_option( 'blog_public', 1 );

	// Hide errors
	ini_set( 'display_errors', 0 );
	define( 'WP_DEBUG', false );
	define( 'WP_DEBUG_DISPLAY', false );
}

/**
 * Path to WordPress
 */
define( 'WP_SITEURL', WP_HOME . '/wp' );

/**
 * Set up databases
 */
foreach ( $database[ WP_STAGE ] as $db_variable => $value ) {
	define( ( 'DB_' . strtoupper( $db_variable ) ), $value );
}
$table_prefix = DB_TBL_PREFIX;

/**
 * Misc. Settings
 */
define( 'WP_POST_REVISIONS', 8 );

/**
 * Custom Content Directory
 */
define( 'WP_CONTENT_DIR', dirname( __FILE__ ) . '/content' );
define( 'WP_CONTENT_URL', 'http://' . $_SERVER['HTTP_HOST'] . '/content' );

/**
 * You almost certainly do not want to change these
 */
define( 'DB_CHARSET', 'utf8' );
define( 'DB_COLLATE', '' );

/**
 * Salts, for security
 */
include dirname( __FILE__ ) . './../config/wp-salts.php';

/**
 * Language
 * Leave blank for American English
 */
define( 'WPLANG', '' );

/**
 * Bootstrap WordPress
 */
if ( !defined( 'ABSPATH' ) )
	define( 'ABSPATH', dirname( __FILE__ ) . '/wp/' );
require_once( ABSPATH . 'wp-settings.php' );
