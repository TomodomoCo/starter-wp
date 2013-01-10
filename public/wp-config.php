<?php

/**
 * Setup the YAML parser, load some yaml files
 */
require_once( dirname( __FILE__ ) . './../vendor/php/yaml/lib/sfYamlParser.php' );
$yaml     = new sfYamlParser();
$project  = $yaml->parse( file_get_contents( dirname( __FILE__ ) . './../config/project.yml' ) );
$database = $yaml->parse( file_get_contents( dirname( __FILE__ ) . './../config/database.yml' ) );

$failure_message = <<<EOT
<html>
<head>
<title>Sorry!</title>
</head>
<body>
<h1>Sorry!</h1>
<p>We are having some trouble loading the site at the moment. Rest assured that the tech support teams have been dispatched and will be fixing this shortly!</p>
<p>Please accept our apologies.</p>
</body>
</html>
EOT;

/**
 * Sanity checking of the imported YAML.
 */
if (
	! is_array( $project ) ||
	! is_array( $database ) ||
	count( $project ) < 1 ||
	count( $database ) < 1 ||
	! array_key_exists( 'domain', $project )
) {
	header('HTTP/1.1 503 Service Unavailable');
	echo $failure_message;
	trigger_error( 'WPFRAME FATAL: === The project.yml and/or database.yml files could not be parsed for the ' . strip_tags( $_SERVER['SERVER_NAME'] ) . ' site.', E_USER_ERROR );
	die();
}

/**
 * Setup the dev, staging, and production environments
 */
$urlParts = explode( '.', $_SERVER['SERVER_NAME'] );
if ( $urlParts[0] == 'dev' ) {
	/**
	 * DEV
	 */
	define( 'WP_STAGE', $urlParts[0] );
	define( 'WP_HOME', 'http://' . WP_STAGE . '.' . $project['domain'] );

	// Make "private"
	define( 'WP_ROBOTS_PUBLIC', 0 );

	// Show errors
	define( 'WP_DEBUG', true );
} elseif ( $urlParts[0] == 'staging' ) {
	/**
	 * STAGING
	 */
	define( 'WP_STAGE', $urlParts[0] );
	define( 'WP_HOME', 'http://' . WP_STAGE . '.' . $project['domain'] );

	// Make "private"
	define( 'WP_ROBOTS_PUBLIC', 0 );

	// Hide errors
	define( 'WP_DEBUG', false );
} else {
	/**
	 * PRODUCTION
	 */
	define( 'WP_STAGE', 'production' );
	define( 'WP_HOME', 'http://www.' . $project['domain'] );

	// Make public
	define( 'WP_ROBOTS_PUBLIC', 1 );

	// Hide errors
	define( 'WP_DEBUG', false );
}

/**
 * Misc. Settings
 */
define( 'WP_POST_REVISIONS', 8 );

/**
 * Language (leave blank for American English)
 */
define( 'WPLANG', '' );

/**
 * Path to WordPress
 */
define( 'WP_SITEURL', WP_HOME . '/wp' );

/**
 * Custom Content Directory
 */
define( 'WP_CONTENT_DIR', dirname( __FILE__ ) . '/content' );
define( 'WP_CONTENT_URL', WP_HOME . '/content' );

/**
 * Debug settings
 */
if ( WP_DEBUG == true ) {
	ini_set( 'display_errors', '1' );
	define( 'WP_DEBUG_DISPLAY', true );
} else {
	ini_set( 'display_errors', '0' );
	define( 'WP_DEBUG_DISPLAY', false );
}

/**
 * Set up databases
 */
if ( array_key_exists( WP_STAGE, $database ) ) {
	foreach ( $database[ WP_STAGE ] as $db_variable => $value ) {
		define( ( 'DB_' . strtoupper( $db_variable ) ), $value );
	}
	$table_prefix = DB_TBL_PREFIX;
} else {
	header('HTTP/1.1 503 Service Unavailable');
	echo $failure_message;
	trigger_error( 'WPFRAME FATAL: === The database.yml file does not have a \'' . strip_tags( WP_STAGE ) . '\' stage, so the DB details cannot be loaded for the ' . strip_tags( $_SERVER['SERVER_NAME'] ) . ' site.', E_USER_ERROR );
	die();
}

/**
 * You almost certainly do not want to change these
 */
define( 'DB_CHARSET', 'utf8' );
define( 'DB_COLLATE', '' );

/**
 * Salts, for security
 */
if ( file_exists( dirname( __FILE__ ) . '/./../config/wp-salts.php' ) ) {
	include dirname( __FILE__ ) . '/./../config/wp-salts.php';
} else {
	trigger_error( 'There is no config/wp-salts.php file for the ' . strip_tags( $_SERVER['SERVER_NAME'] ) . ' site.' , E_USER_WARNING );
}

/**
 * Bootstrap WordPress
 */
if ( !defined( 'ABSPATH' ) )
	define( 'ABSPATH', dirname( __FILE__ ) . '/wp/' );
require_once( ABSPATH . 'wp-settings.php' );

/**
 * Set 'blog_public'
 */
if ( defined( 'WP_ROBOTS_PUBLIC' ) )
	update_option( 'blog_public', WP_ROBOTS_PUBLIC );
