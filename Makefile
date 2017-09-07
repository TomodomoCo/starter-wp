install:
	bundle
	yarn install

assets: install
	yarn run bower install
	yarn run gulp

salts:
	echo '<?php' > config/wp-salts.php && curl https://api.wordpress.org/secret-key/1.1/salt >> config/wp-salts.php

.PHONY: assets salts
