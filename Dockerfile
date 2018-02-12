FROM python:3.5.5-jessie

# TODO: move in a base image
RUN useradd -ms /bin/bash -G www-data elife && \
    chown elife:elife /srv && \
    mkdir /srv/bin && \
    chown elife:elife /srv/bin && \
    mkdir -p /var/www && \
    chown www-data:www-data /var/www

RUN pip install -U virtualenv
RUN pip install -U setuptools
# END base image

USER elife
ENV PROJECT_FOLDER=/srv/profiles
ENV LANG=en_US.UTF-8
RUN mkdir ${PROJECT_FOLDER}
WORKDIR /srv/profiles
COPY --chown=elife:elife install.sh requirements.txt /srv/profiles/
RUN PROFILES_SKIP_DB=1 /bin/bash install.sh

## yes this is how you copy directories
COPY --chown=elife:elife manage.py /srv/profiles/
COPY --chown=elife:elife migrations /srv/profiles/
COPY --chown=elife:elife profiles/ /srv/profiles/profiles

RUN mkdir -p var/logs
USER root
RUN chown www-data:www-data var/logs

USER www-data
ENTRYPOINT ["venv/bin/python"]
