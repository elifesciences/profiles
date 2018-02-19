#!/usr/bin/env bash
set -e

source venv/bin/activate

python -m proofreader manage.py profiles/ test/
coverage run -m pytest --junitxml=build/pytest.xml

coveralls
