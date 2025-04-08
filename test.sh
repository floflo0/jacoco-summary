#!/usr/bin/bash

set -xe

mypy
coverage run --branch -m pytest --verbose --no-header
coverage report --show-missing --skip-covered --omit=test/*
pylint jacoco_summary test
