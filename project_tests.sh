#!/usr/bin/env bash
set -e

source venv/bin/activate

pylint -r n profiles/ test/*.py
python -m pytest --junitxml=build/pytest.xml
