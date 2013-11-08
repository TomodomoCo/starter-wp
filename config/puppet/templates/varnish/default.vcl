#
#
# Global default.vcl
#
#

backend default {
	.host = "127.0.0.1";
	.port = "8080";
}

acl purge {
	"localhost";
}

sub identify_ua {
	# detect the device type, so we can cache mobile and regular pages separately

	if (req.http.User-Agent ~ "Mobile/") {
		set req.http.X-Device = "mobile";
	}
	else {
		set req.http.X-Device = "default";
	}

}

sub vcl_recv {

	# global recv rules

	# allow localhost to PURGE the cache
	if (req.request == "PURGE") {
		if (!client.ip ~ purge) {
			error 405 "Not allowed.";
		}
		return(lookup);
	}

	# global WP-Admin always to pass
	if (req.url ~ "^/(?:wp/)?wp-admin/.*$") {
		return(pass);
	}

	# global wp-*.php always to pass
	if (req.url ~ "^/(?:wp/)?wp-(.*).php$") {
		return(pass);
	}

	# do not cache the feed for FeedBurner
	if (req.url ~ "feed/.*$" && req.http.user-agent ~ "^FeedBurner/")
	{
		return(pass);
	}

	# run site-specific rules
	include "/etc/varnish/sites-recv.vcl";

}

sub vcl_hash {

	# identify mobile
	call identify_ua;

	hash_data(req.url);

	if (req.http.host) {
		hash_data(req.http.host);
	}
	else {
		hash_data(server.ip);
	}

	# cache differently for Mobile/ vs. default
	hash_data(req.http.X-Device);

	return(hash);

}

sub vcl_fetch {

	if ( beresp.status >= 500 )
	{
		# do not cache errors!
		set beresp.ttl = 0s;
	}

	# if no cache-control info, set some sensible defaults
	if (beresp.ttl > 0s && !beresp.http.cache-control) {
		set beresp.http.cache-control = "max-age=180, must-revalidate";
	}
	

	# run site-specific rules
	include "/etc/varnish/sites-fetch.vcl";

}

sub vcl_hit {

	if (req.request == "PURGE") {
		purge;
		error 200 "Purged.";
	}
	
}

sub vcl_miss {
	if (req.request == "PURGE") {
		purge;
		error 200 "Purged.";
	}
}

sub vcl_deliver {
	remove resp.http.X-Powered-By;
	remove resp.http.WP-Super-Cache;

	# if the magic marker for Age resetting is set, then reset the Age
	if (resp.http.X-VPM-Is-New-Object) {
		remove resp.http.X-VPM-Is-New-Object;
		set resp.http.age = "0";
	}

	set resp.http.X-VPM-Served = "pongo";

	set resp.http.X-VPM-Cache = obj.hits;

	return(deliver);

}

# TODO -- pretty vcl_error?
