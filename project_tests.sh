#!/usr/bin/env bash
set -e

proofreader --targets manage.py profiles/ test/
coverage run -m pytest --junitxml=build/pytest.xml

coveralls
