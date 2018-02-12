ARG commit=latest
FROM elifesciences/profiles_cli:${commit}

ENTRYPOINT ["venv/bin/uwsgi", "--ini=/srv/profiles/uwsgi.ini"]
