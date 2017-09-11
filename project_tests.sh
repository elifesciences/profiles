#!/usr/bin/env bash
set -e

source venv/bin/activate

pylint -r n profiles/ test/*.py
flake8 profiles/ test/
python -m pytest --junitxml=build/pytest.xml
