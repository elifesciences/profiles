eLife Profiles
==============

[![Build Status](https://ci--alfred.elifesciences.org/buildStatus/icon?job=test-profiles)](https://ci--alfred.elifesciences.org/job/test-profiles/) [![Coverage Status](https://coveralls.io/repos/github/elifesciences/profiles/badge.svg?branch=develop)](https://coveralls.io/github/elifesciences/profiles?branch=develop)

Profiles is a service used by eLife Sciences Publications, Ltd. to create and 
store eLife user profiles. Currently, eLife uses [ORCID](https://orcid.org/) for 
authentication.

When a user account is created or updated on ORCID, the new account information is sent to 
the Profiles service via a webhook and a new eLife profile is created, ready to be
used by other services.

End points
----------
- `/ping` returns the message `pong` *(useful for testing connection to the service)*
- `/profiles` returns a list of profiles *(See [Here](https://api.elifesciences.org) for more information)*
- `/profiles/<profile_id>` returns a given profile *(See [Here](https://api.elifesciences.org) for more information)*
 
Development
===========

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