eLife Profiles
==============

[![Build Status](https://ci--alfred.elifesciences.org/buildStatus/icon?job=test-profiles)](https://ci--alfred.elifesciences.org/job/test-profiles/)

Dependencies
------------

* [Python](https://www.python.org/)

Installation
------------

1. Create `app.cfg` from `app.cfg.dist`
2. `./install.sh`

Running the tests
-----------------

```
./project_tests.sh
```

Running the site
----------------

```
source venv/bin/activate
python manage.py runserver
```

*Note in production [use a proper server](http://flask.pocoo.org/docs/0.12/deploying/uwsgi/).*
