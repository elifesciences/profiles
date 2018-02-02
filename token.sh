#!/bin/bash
set -e

file=${1:-sample}.log
status=$(curl -o $file -s -w '%{http_code}' localhost/oauth2/token -d 'client_id=foo&client_secret=bar&redirect_uri=https://example.com/check&grant_type=authorization_code&code=1234')
if [ "$status" != "200" ]; then
    cat $file
    exit 1
fi

