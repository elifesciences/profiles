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
docker-compose run --rm ci venv/bin/pytest
```

Running the site
----------------

```
docker-compose up -d
curl -v localhost:8080/ping  # 'pong'
```

Update a package
-----------------

You [can't upgrade a single package at the moment](https://github.com/pypa/pipenv/issues/966). If there is something that must not be upgraded, pin an appropriate major, minor, or patch version in the `Pipfile`.

This is a reproducible workflow for a global update:
```
docker-compose build
docker rm profiles_venv_update
docker-compose run --name=profiles_venv_update venv /bin/bash -c 'source venv/bin/activate && pipenv update'
docker cp profiles_venv_update:/srv/profiles/Pipfile.lock .
```

Local virtual environment (for IDE usage)
-----------------------------------------

Experimental:

```
docker cp profiles_ci_1:/srv/profiles/venv/ .
```
