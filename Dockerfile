FROM elifesciences/python:b22fbad8f66100d88cb4bd7c7d092b376a9e09bc

ENV LANG=C.UTF-8

USER root
RUN pip install -U pipenv

USER elife
ENV PROJECT_FOLDER=/srv/profiles
ENV PIPENV_VENV_IN_PROJECT=true
RUN mkdir ${PROJECT_FOLDER}
WORKDIR ${PROJECT_FOLDER}

COPY --chown=elife:elife Pipfile Pipfile.lock /srv/profiles/
RUN pipenv install --deploy

USER elife
COPY --chown=elife:elife manage.py /srv/profiles/
COPY --chown=elife:elife migrations/ /srv/profiles/migrations/
COPY --chown=elife:elife profiles/ /srv/profiles/profiles/
COPY --chown=elife:elife smoke_tests_wsgi.sh /srv/profiles/
RUN mkdir /srv/profiles/var/

USER root
RUN mkdir var/logs && chown www-data:www-data var/logs

USER www-data
CMD [".venv/bin/python"]

ARG dependencies_orcid_dummy
LABEL org.elifesciences.dependencies.orcid-dummy="${dependencies_orcid_dummy}"
