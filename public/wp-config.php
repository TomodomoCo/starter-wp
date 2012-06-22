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
	define('WP_CACHE', true); //Added by WP-Cache Manager
	define( 'WP_STAGE', 'dev' );
	foreach($config['dev'] as $db_variable => $value) {
		define(('DB_' . strtoupper($db_variable)), $value);
	}
} elseif ($urlParts[0] == 'staging') {
	// Staging
	define('WP_CACHE', true); //Added by WP-Cache Manager
	define( 'WP_STAGE', 'staging' );
	define( 'DB_CLIENT_FLAGS', MYSQL_CLIENT_SSL );
	foreach($config['staging'] as $db_variable => $value) {
		define(('DB_' . strtoupper($db_variable)), $value);
	}
} else {
	// Production
	define('WP_CACHE', true); //Added by WP-Cache Manager
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
define('AUTH_KEY',         '7{sH-wO(O~qLO( O]/X2c9fS zds?7ev:Q~I(CxXq+$+sRr6/Np-#.<]!oHy8f(y');
define('SECURE_AUTH_KEY',  'ITQl5zJ<3;s>H~f{PvFRtSu*2|`}n2$N?VN|6/d}}Du&4,gi7Yk|S~APL9`UlmU6');
define('LOGGED_IN_KEY',    'o:Fzq>,?&9*:X{]sD:F1t<3yR:~Kcf:#},)~ZJ<pbT*|Z!(]h[LDX|sWumDc=s-t');
define('NONCE_KEY',        'LW;&ms-Im=H1UND[e}+X-Y`(d$h,+gb2-m?(Ap`ftgA+U+(K#lwq gqa-7+UPoJ[');
define('AUTH_SALT',        'Va|MFYP6rv[qLN:!E#j6;}VNn8 7Y`>Ug-+3=&s#aB(AZp$_}5I*XoG#1$Ns;TCU');
define('SECURE_AUTH_SALT', 'RsVI0P+:=>3?+-uTJGURJo=|CS9.yNM3x|pLs_yw-52s-`cfgn@KV)4a<b_iy_gq');
define('LOGGED_IN_SALT',   'uGz04dTP/@GL|^z-0lnINGw}!}U2,n9+N.~%Y+MvV!<v_+%.-_ALm/cZN`:Kkte ');
define('NONCE_SALT',       '?6/j&QU`+0rNoSl8H4B5g~n0)dTPm+_)%_Ti. !tmM/ChPzo(GiDEh64]u|%_Ot3');

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