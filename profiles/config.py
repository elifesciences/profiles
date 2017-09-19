from abc import ABC
from configparser import RawConfigParser
from typing import Dict


class Config(ABC):
    DEBUG = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = False

    def __init__(self, orcid: Dict[str, str], db: str, logging: Dict[str, str]) -> None:
        self.orcid = orcid
        self.SQLALCHEMY_DATABASE_URI = db  # pylint: disable=invalid-name
        self.logging = logging


class DevConfig(Config):
    DEBUG = True
    name = 'dev'


class CiConfig(DevConfig):
    TESTING = True
    name = 'ci'


class ProdConfig(Config):
    name = 'prod'


class ContinuumTestConfig(ProdConfig):
    name = 'continuumtest'


class End2EndConfig(ProdConfig):
    name = 'end2end'


ENVIRONMENTS = {
    'dev': DevConfig,
    'ci': CiConfig,
    'prod': ProdConfig,
    'continuumtest': ContinuumTestConfig,
    'end2end': End2EndConfig,
}


def create_app_config(config: RawConfigParser) -> Config:
    kwargs = {section: dict(config.items(section)) for section in config.sections()}
    kwargs = {**kwargs.pop('profiles', {}), **kwargs}
    environment = kwargs.pop('environment', 'dev')

    return ENVIRONMENTS[environment](**kwargs)
