ARG commit=latest
FROM elifesciences/profiles_cli:${commit}

ENV LANG=en_US.UTF-8
ENTRYPOINT ["venv/bin/uwsgi", "--ini=/srv/profiles/uwsgi.ini"]
