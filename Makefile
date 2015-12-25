install:
	bundle
	npm install

assets: install
	npm run bower install
	npm run gulp

.PHONY: assets
