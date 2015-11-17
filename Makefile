COMPILED = ./public/assets

assets:
	npm install
	bower install
	gulp

ports:
	sudo pfctl -evf config/pf.conf

clean: clean-css clean-javascripts clean-images

clean-css:
	rm -rf $(COMPILED)/css/

clean-javascripts:
	rm -rf $(COMPILED)/js/

clean-images:
	rm -rf $(COMPILED)/img/

.PHONY: assets clean clean-css clean-javascripts clean-images
