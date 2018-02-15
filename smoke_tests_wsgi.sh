#!/usr/bin/env bash
set -ex

host=${1:-profiles}

wait_for_port 5432 15 db
uwsgi_curl 127.0.0.1:9000 "${host}/ping"
uwsgi_curl 127.0.0.1:9000 "${host}/profiles"
