#!/usr/bin/env bash
set -e

source venv/bin/activate
export PYTHONOPTIMIZE=

coverage run -m pytest --junitxml=build/pytest.xml
