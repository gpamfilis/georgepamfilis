#!/usr/bin/env bash
git fetch --all
git reset --hard origin/master
rm test.db
rm -rf migrations/
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
