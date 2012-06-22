<?php
class custom_wpdb extends wpdb {
	/**
	 * Copy of the db_connect function with definable newlink and client_flags params
	 */
	function db_connect() {

		$this->is_mysql = true;

		if ( defined( 'DB_NEW_LINK' ) ) 
			$this->newlink = DB_NEW_LINK; 
		else  
			$this->newlink = true; 

		if ( defined( 'DB_CLIENT_FLAGS' ) )  
			$this->client_flags = DB_CLIENT_FLAGS; 
		else 
			$this->client_flags = 0; 


		if ( WP_DEBUG ) {
			$this->dbh = mysql_connect( $this->dbhost, $this->dbuser, $this->dbpassword, $this->newlink, $this->client_flags );
		} else {
			$this->dbh = @mysql_connect( $this->dbhost, $this->dbuser, $this->dbpassword, $this->newlink, $this->client_flags );
		}

		if ( !$this->dbh ) {
			wp_load_translations_early();
			$this->bail( sprintf( __( "
<h1>Error establishing a database connection</h1>
<p>This either means that the username and password information in your <code>wp-config.php</code> file is incorrect or we can't contact the database server at <code>%s</code>. This could mean your host's database server is down.</p>
<ul>
	<li>Are you sure you have the correct username and password?</li>
	<li>Are you sure that you have typed the correct hostname?</li>
	<li>Are you sure that the database server is running?</li>
</ul>
<p>If you're unsure what these terms mean you should probably contact your host. If you still need help you can always visit the <a href='http://wordpress.org/support/'>WordPress Support Forums</a>.</p>
" ), htmlspecialchars( $this->dbhost, ENT_QUOTES ) ), 'db_connect_fail' );

			return;
		}

		$this->set_charset( $this->dbh );

		$this->ready = true;

		$this->select( $this->dbname, $this->dbh );
	}
}

global $wpdb;
$wpdb = new custom_wpdb( DB_USER, DB_PASSWORD, DB_NAME, DB_HOST );