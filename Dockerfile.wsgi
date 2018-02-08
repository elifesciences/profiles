ARG commit=latest
FROM elifesciences/profiles:${commit}

ENTRYPOINT ["venv/bin/uwsgi"]
