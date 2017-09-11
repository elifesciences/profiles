#!/usr/bin/env bash
set -e

source venv/bin/activate

pylint --reports=n profiles/ test/*.py
python -m pytest --junitxml=build/pytest.xml
