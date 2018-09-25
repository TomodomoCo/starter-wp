<?php

// Get the directory
$dir = dirname(__FILE__);

/**
 * Require the Composer autoloader
 */
require_once("{$dir}/../vendor/composer/autoload.php");


/**
 * Setup the YAML parser, load some yaml files
 */
use Symfony\Component\Yaml\Parser;
$yaml     = new Parser();
$project  = $yaml->parse(file_get_contents("{$dir}/../config/project.yml"));
$database = $yaml->parse(file_get_contents("{$dir}/../config/secrets/database.yml"));

/**
 * Throw an error if things break
 */
$failure_message = <<<EOT
<html>
    <head><title>Sorry!</title></head>
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
	!is_array($project) ||
	!is_array($database) ||
	count($project) < 1 ||
    count($database) < 1 )
{
	header('HTTP/1.1 503 Service Unavailable');

	echo $failure_message;

	trigger_error( 'WPFRAME FATAL: The project.yml and/or database.yml files could not be parsed for the ' . strip_tags( $_SERVER['SERVER_NAME'] ) . ' site.', E_USER_ERROR );

	die;
}

/**
 * Setup the dev, staging, and production environments
 */
if ($_SERVER['SERVER_NAME'] === $project['stage']['dev']['domain']) {

	/**
	 * DEV
	 */
	define('WP_STAGE', 'dev');
	define('WP_HOME', "http://{$project['stage']['dev']['domain']}");

	// Make "private"
	define('WP_ROBOTS_PUBLIC', 0);

	// Show errors
	define('WP_DEBUG', true);

} elseif ($_SERVER['SERVER_NAME'] === $project['stage']['staging']['domain']) {

	/**
	 * STAGING
	 */
	define('WP_STAGE', 'staging');
	define('WP_HOME', "http://{$project['stage']['staging']['domain']}");

	// Make "private"
	define('WP_ROBOTS_PUBLIC', 0);

	// Hide errors
	define('WP_DEBUG', false);

} else {

	/**
	 * PRODUCTION
	 */
	define('WP_STAGE', 'production');
	define('WP_HOME', "https://{$project['stage'][WP_STAGE]['domain']}");

	// Make public
	define('WP_ROBOTS_PUBLIC', 1);

	// Hide errors
	define('WP_DEBUG', false);

}

/**
 * Misc. Settings
 */
define('WP_POST_REVISIONS', 8); // Post revisions to store
define('WPLANG', '');           // Language (leave blank for American English)
define('WP_SITEURL', WP_HOME);  // Base URL for wp-admin

/**
 * Custom Content Directory
 */
define('WP_CONTENT_DIR', "{$dir}/content");
define('WP_CONTENT_URL', WP_HOME . '/content');

/**
 * Debug settings
 */
if (WP_DEBUG === true) {
	ini_set('display_errors', '1');
	define('WP_DEBUG_DISPLAY', true);
} else {
	ini_set('display_errors', '0');
	define('WP_DEBUG_DISPLAY', false);
}

/**
 * Set up databases
 */
if (array_key_exists(WP_STAGE, $database)) {
	foreach ($database[WP_STAGE] as $db_variable => $value) {
		define(('DB_' . strtoupper($db_variable)), $value);
	}

	$table_prefix = DB_TBL_PREFIX;
} else {
	header('HTTP/1.1 503 Service Unavailable');

	echo $failure_message;

	trigger_error('WPFRAME FATAL: The database.yml file does not have a `' . strip_tags(WP_STAGE) . '` stage, so the DB details cannot be loaded for the `' . strip_tags($_SERVER['SERVER_NAME']) . '` site.', E_USER_ERROR);

	die;
}

/**
 * You almost certainly do not want to change these
 */
define('DB_CHARSET', 'utf8');
define('DB_COLLATE', '');

/**
 * Salts, for security
 */
if (file_exists("{$dir}/../config/secrets/wp-salts.php")) {
	include "{$dir}/../config/secrets/wp-salts.php";
} else {
	trigger_error('There is no config/secrets/wp-salts.php file for the ' . strip_tags($_SERVER['SERVER_NAME']) . ' site.' , E_USER_WARNING);
}

/**
 * Bootstrap WordPress
 */
if (!defined('ABSPATH')) {
	define('ABSPATH', "{$dir}/wp/");
}

require_once(ABSPATH . 'wp-settings.php');
