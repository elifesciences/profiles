#!/bin/bash
set -e

cd /srv/orcid-dummy
git checkout master
git pull origin master
new_commit=$(git rev-parse origin/master)
cd -
echo $new_commit > orcid-dummy.sha1

