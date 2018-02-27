#!/usr/bin/env bash
set -ex

host=${1:-profiles}
db=${2:-db}

wait_for_port 5432 15 "${db}"
uwsgi_curl 127.0.0.1:9000 "${host}/ping"
uwsgi_curl 127.0.0.1:9000 "${host}/profiles"
if [ "$ENVIRONMENT_NAME" = 'dev' ]; then
    [ "$(uwsgi_curl 127.0.0.1:9000 "${host}/oauth2/authorize?client_id=client_id&response_type=code" | grep 'HTTP/1.1' | tr -d '\n\r')" = 'HTTP/1.1 302 FOUND' ]
    [ "$(uwsgi_curl 127.0.0.1:9000 "${host}/oauth2/check?code=12345&state=%7B%22client_id%22%3A%22client_id%22%2C%22original%22%3A%2212345678901234567890%22%2C%22redirect_uri%22%3A%22http%3A%2F%2Fwww.example.com%2Fcheck%22%7D" | grep 'HTTP/1.1' | tr -d '\n\r')" = 'HTTP/1.1 302 FOUND' ]
fi
