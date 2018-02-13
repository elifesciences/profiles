#!/usr/bin/env bash
set -e

echo "[-] install.sh"

if [ ! -e "venv/bin/python3.5" ]; then
    echo "could not find venv/bin/python3.5, recreating venv"
    rm -rf venv
    virtualenv --python=python3.5 venv
fi

source venv/bin/activate

if pip list | grep api-validator-python; then
    pip uninstall -y api-validator-python
fi

pip install --requirement requirements.txt
if [ -z "$PROFILES_SKIP_DB" ]; then
    python manage.py db upgrade
fi

echo "[✓] install.sh"
