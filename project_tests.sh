#!/usr/bin/env bash
set -e

source venv/bin/activate
export PYTHONOPTIMIZE=

proofreader --targets manage.py profiles/ test/
coverage run -m pytest --junitxml=build/pytest.xml

coveralls
