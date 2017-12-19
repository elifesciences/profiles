#!/usr/bin/env bash
set -e

source venv/bin/activate

pip install coveralls
pip install proofreader==0.0.2

python -m proofreader manage.py profiles/ test/
coverage run -m pytest --junitxml=build/pytest.xml

COVERALLS_REPO_TOKEN=$(cat /etc/coveralls/tokens/profiles) coveralls
