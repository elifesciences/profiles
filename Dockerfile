ARG image_tag=latest
FROM elifesciences/profiles_venv:${image_tag} as venv
FROM elifesciences/python:b22fbad8f66100d88cb4bd7c7d092b376a9e09bc

ENV PROJECT_FOLDER=/srv/profiles
WORKDIR ${PROJECT_FOLDER}

USER root
RUN mkdir -p var/logs && \
    chown --recursive elife:elife . && \
    chown www-data:www-data var/logs

COPY --chown=elife:elife smoke_tests_wsgi.sh ./
COPY --chown=elife:elife manage.py ./
COPY --chown=elife:elife migrations/ migrations/
COPY --from=venv --chown=elife:elife ${PROJECT_FOLDER}/venv/ venv/
COPY --chown=elife:elife profiles/ profiles/

USER www-data
CMD ["venv/bin/python"]

ARG dependencies_orcid_dummy
LABEL org.elifesciences.dependencies.orcid-dummy="${dependencies_orcid_dummy}"
