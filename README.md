eLife Profiles
==============

[![Build Status](https://ci--alfred.elifesciences.org/buildStatus/icon?job=test-profiles)](https://ci--alfred.elifesciences.org/job/test-profiles/) [![Coverage Status](https://coveralls.io/repos/github/elifesciences/profiles/badge.svg?branch=develop)](https://coveralls.io/github/elifesciences/profiles?branch=develop)

Dependencies
------------

* [Python 3.5](https://www.python.org/)
* [virtualenv](https://virtualenv.pypa.io/)

Installation
------------

1. Create `app.cfg` from `app.cfg.dist`
2. Create `clients.yaml` from `clients.yaml.dist`
3. `./install.sh`

Running the tests
-----------------

```
docker-compose -f docker-compose.yml -f docker-compose.ci.yml build
docker-compose -f docker-compose.yml -f docker-compose.ci.yml run --rm ci venv/bin/pytest
```

Running the site
----------------

```
docker-compose up -d
curl -v localhost:8080/ping  # 'pong'
```

Local virtual environment (for IDE usage)
-----------------------------------------

Experimental:

```
docker cp profiles_ci_1:/srv/profiles/venv/ .
```
