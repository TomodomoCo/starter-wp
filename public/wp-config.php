<?php
// ===================================================
// Load database info and local development parameters
// ===================================================

require_once(dirname(__FILE__).'./../vendor/php/yaml/lib/sfYamlParser.php');
$yaml = new sfYamlParser();
$config = $yaml->parse(file_get_contents(dirname(__FILE__).'./../config/database.yml'));

$urlParts = explode('.', $_SERVER['HTTP_HOST']);
if ($urlParts[0] == 'dev') {
	// Local dev
	define( 'WP_STAGE', 'dev' );
	foreach($config['dev'] as $db_variable => $value) {
		define(('DB_' . strtoupper($db_variable)), $value);
	}
} elseif ($urlParts[0] == 'staging') {
	// Staging
	define( 'WP_STAGE', 'staging' );
	define( 'DB_CLIENT_FLAGS', MYSQL_CLIENT_SSL );
	foreach($config['staging'] as $db_variable => $value) {
		define(('DB_' . strtoupper($db_variable)), $value);
	}
} else {
	// Production
	define( 'WP_STAGE', 'production' );
	define( 'DB_CLIENT_FLAGS', MYSQL_CLIENT_SSL );
	foreach($config['production'] as $db_variable => $value) {
		define(('DB_' . strtoupper($db_variable)), $value);
	}
}

// ==============
// Misc. Settings
// ==============
define('WP_POST_REVISIONS', 8);

// ========================
// Custom Content Directory
// ========================
define( 'WP_CONTENT_DIR', dirname( __FILE__ ) . '/content' );
define( 'WP_CONTENT_URL', 'http://' . $_SERVER['HTTP_HOST'] . '/content' );

// ================================================
// You almost certainly do not want to change these
// ================================================
define( 'DB_CHARSET', 'utf8' );
define( 'DB_COLLATE', '' );

// ==============================================================
// Salts, for security
// Grab these from: https://api.wordpress.org/secret-key/1.1/salt
// ==============================================================
define('AUTH_KEY',         'add');
define('SECURE_AUTH_KEY',  'your');
define('LOGGED_IN_KEY',    'own');
define('NONCE_KEY',        'damn');
define('AUTH_SALT',        'salts');
define('SECURE_AUTH_SALT', 'here');
define('LOGGED_IN_SALT',   'mmk?');
define('NONCE_SALT',       'https://api.wordpress.org/secret-key/1.1/salt/');

// ============
// Table prefix
// ============
$table_prefix  = 'wp_';

// ================================
// Language
// Leave blank for American English
// ================================
define( 'WPLANG', '' );

// ===========
// Hide errors
// ===========
ini_set( 'display_errors', 0 );
define( 'WP_DEBUG_DISPLAY', false );

// ===================
// Bootstrap WordPress
// ===================
if ( !defined( 'ABSPATH' ) )
	define( 'ABSPATH', dirname( __FILE__ ) . '/wp/' );
require_once( ABSPATH . 'wp-settings.php' );