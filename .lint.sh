#!/bin/bash
set -e

source venv/bin/activate

pylint --errors-only manage.py profiles/ test/ --rcfile=.pylintrc

black profiles/ test/ --target-version py38
