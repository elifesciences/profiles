FROM python:3.5.5-jessie

# TODO: move in a base image
RUN useradd -ms /bin/bash -G www-data elife && \
    chown elife:elife /srv && \
    mkdir /srv/bin && \
    chown elife:elife /srv/bin && \
    mkdir -p /var/www && \
    chown www-data:www-data /var/www

RUN apt-get update && apt-get install -y virtualenv
# END base image

USER elife
ENV PROJECT_FOLDER=/srv/profiles
RUN mkdir ${PROJECT_FOLDER}
WORKDIR /srv/profiles
# workaround for Alembic failing installation
#RUN virtualenv --python=python3.5 venv \
#    && venv/bin/pip install -U setuptools
# end of workaround
COPY --chown=elife:elife install.sh requirements.txt /srv/profiles/
RUN PROFILES_SKIP_DB=1 /bin/bash install.sh

## yes this is how you copy directories
#COPY --chown=elife:elife src/ /srv/profiles/src
#...
#
#RUN mkdir -p var/logs
#USER root
#RUN chown www-data:www-data var/logs var/cache/html_purifier
#
USER www-data
#CMD ["venv/bin/uwsgi", "/console", "queue:watch"]
