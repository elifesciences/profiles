eLife Profiles
==============

[![Build Status](https://ci--alfred.elifesciences.org/buildStatus/icon?job=test-profiles)](https://ci--alfred.elifesciences.org/job/test-profiles/) [![Coverage Status](https://coveralls.io/repos/github/elifesciences/profiles/badge.svg?branch=develop)](https://coveralls.io/github/elifesciences/profiles?branch=develop)

Dependencies
------------

* [Docker](https://www.docker.com/)

Running the site locally
------------------------

```
make start
```
This command will build and run the site locally for development purposes.

```
make stop
```
Use this command to stop containers and clean up any anonymous volumes.

Running the tests
-----------------
Use this command when writing and running tests for development purposes:
```
make tests
```

Use this command to run tests using production settings (typically used for running tests in CI pipeline)
```
docker-compose -f docker-compose.yml -f docker-compose.ci.yml run --rm ci venv/bin/pytest
```

Make commands
-------------
For a full list of make commands run:
```
make help
```