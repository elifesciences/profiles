#!/usr/bin/env bash
set -e

echo "[-] install.sh"

if [ ! -e "venv/bin/python3.5" ]; then
    echo "could not find venv/bin/python3.5, recreating venv"
    rm -rf venv
    virtualenv --python=python3.5 venv
fi

source venv/bin/activate

pip install --requirement requirements.txt

echo "[✓] install.sh"
