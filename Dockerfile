FROM elifesciences/python:889f7fa7844074ed4791084624ee19b40db258a0

USER elife
ENV PROJECT_FOLDER=/srv/profiles
RUN mkdir ${PROJECT_FOLDER}
WORKDIR /srv/profiles
COPY --chown=elife:elife install.sh requirements.txt /srv/profiles/
RUN PROFILES_SKIP_DB=1 /bin/bash install.sh

COPY --chown=elife:elife manage.py /srv/profiles/
COPY --chown=elife:elife migrations/ /srv/profiles/migrations/
COPY --chown=elife:elife profiles/ /srv/profiles/profiles/
COPY --chown=elife:elife smoke_tests_wsgi.sh /srv/profiles/
RUN mkdir /srv/profiles/var/

USER root
RUN mkdir var/logs && chown www-data:www-data var/logs

USER www-data
CMD ["venv/bin/python"]

ARG dependencies_orcid_dummy
LABEL org.elifesciences.dependencies.orcid-dummy="${dependencies_orcid_dummy}"
