RAW = ./app/assets
COMPILED = ./public/assets

assets: images javascripts css

css:
	compass compile

javascripts:
	jammit

images:
	mkdir -p $(COMPILED)/img/
	cp -R $(RAW)/images/. $(COMPILED)/img/
	image_optim --recursive --no-pngout $(COMPILED)/img/

clean: clean-css clean-javascripts clean-images

clean-css:
	rm -rf $(COMPILED)/css/

clean-javascripts:
	rm -rf $(COMPILED)/js/

clean-images:
	rm -rf $(COMPILED)/img/

.PHONY: assets css javascripts images clean clean-css clean-javascripts clean-images
