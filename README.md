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
docker-compose run --rm cli venv/bin/pytest
```

For `proofreader` static checks:

```
docker-compose run cli /bin/bash -c 'source venv/bin/activate && venv/bin/proofreader --targets manage.py profiles/ test/'
```

Running the site
----------------

```
docker-compose up -d
curl -v localhost:8080/ping  # 'pong'
```

Local virtual environment (for IDE usage)
-----------------------------------------

Experimental (`sudo` necessary due to `root` ownership):

```
sudo docker cp profiles_cli_1:/srv/profiles/venv .
```
