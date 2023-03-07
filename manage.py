import sys
from flask.cli import main

if __name__ == '__main__':
    # ["manage.py", "--app", "app", "foo", "bar", "baz", ...]
    sys.argv = sys.argv[:1] + ["--app", "app"] + sys.argv[1:]
    sys.exit(main())
