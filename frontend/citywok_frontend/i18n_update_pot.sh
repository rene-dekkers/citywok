#!/bin/bash
VERSION=$(grep ^__version__ __init__.py | awk -F '=' '{print $2}' | tr -d '[:space:]')
OPTIONS="--sort-output --msgid-bugs-address=rene@dekkers.biz --copyright-holder='Rene\ Dekkers' --project=CityWok --version=$VERSION"
pybabel-python3 extract \
	--sort-output \
	--msgid-bugs-address=rene@dekkers.biz \
	--copyright-holder="Rene Dekkers" \
	--project=CityWok \
	--version="$VERSION" \
	-F babel.cfg \
	-o messages.pot .
pybabel-python3 update -i messages.pot -d translations
