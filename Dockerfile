FROM python:3.5.5-jessie

# TODO: move in a base image
ENV LANG=en_US.UTF-8
ENV PATH=/srv/bin:${PATH}
RUN useradd -ms /bin/bash -G www-data elife && \
    chown elife:elife /srv && \
    mkdir /srv/bin && \
    chown elife:elife /srv/bin && \
    mkdir -p /var/www && \
    chown www-data:www-data /var/www

RUN pip install -U \
    setuptools \
    uwsgi-tools \
    virtualenv
RUN apt-get update && apt-get install netcat-openbsd
COPY --chown=elife:elife wait_for_port /srv/bin/
# END base image

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
