#!/bin/bash
set -e

file=${1:-sample}.log
status=$(curl -o $file -s -w '%{http_code}' localhost:8080/oauth2/token -d 'client_id=client_id&client_secret=client_secret&redirect_uri=http://www.example.com/check&grant_type=authorization_code&code=1234')
if [ "$status" != "200" ]; then
    cat $file
    exit 1
fi

