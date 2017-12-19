#!/usr/bin/env bash
set -e

source venv/bin/activate

pip install proofreader==0.0.2

python -m proofreader manage.py profiles/ test/
python -m pytest --junitxml=build/pytest.xml
