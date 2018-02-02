#!/bin/bash
set -e

rm -f *.log
sudo systemctl restart uwsgi-profiles
while true; do
    echo "Clear data"
    venv/bin/python manage.py clear 2>/dev/null
    echo "Two parallel profile creations"
    printf "a\nb\n" | xargs \
        -I {} \
        -P 2 \
        ./token.sh {}
done
