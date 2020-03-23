#!/usr/bin/env sh

rm db.sqlite
rm -rf migrations/versions/*

flask db migrate
flask db upgrade
flask import-test-data