#!/usr/bin/env bash
set -ex

host=${1:-profiles}

wait_for_port 5432 15 db
uwsgi_curl 127.0.0.1:9000 "${host}/ping"
uwsgi_curl 127.0.0.1:9000 "${host}/profiles"
[ "$(uwsgi_curl 127.0.0.1:9000 "${host}/oauth2/authorize?client_id=client_id&response_type=code" | grep 'HTTP/1.1' | tr -d '\n\r')" = 'HTTP/1.1 302 FOUND' ]
