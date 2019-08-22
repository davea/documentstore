#!/bin/sh

export LANG=en_GB.UTF-8
export LC_ALL=en_GB.UTF-8
export DJANGO_SETTINGS_MODULE=documentstore.settings.production
export PATH=/bin:/usr/bin:/usr/local/bin

set -e
cd "$(dirname "$0")/.."

pipenv run python manage.py doxie_import $1
