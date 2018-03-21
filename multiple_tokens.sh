#!/bin/bash
set -e

rm -f *.log
docker-compose up -d --force-recreate
while true; do
    echo "Clear data"
    docker-compose run --rm wsgi venv/bin/python manage.py clear >/dev/null
    echo "Two parallel profile creations"
    printf "a\nb\n" | xargs \
        -I {} \
        -P 2 \
        ./token.sh {}
done
