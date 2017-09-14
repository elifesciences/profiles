from abc import ABC
from configparser import RawConfigParser
from typing import Dict


class Config(ABC):
    DEBUG = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = False

    def __init__(self, orcid: Dict[str, str], db: str) -> None:
        self.orcid = orcid
        self.SQLALCHEMY_DATABASE_URI = db  # pylint: disable=invalid-name


class DevConfig(Config):
    DEBUG = True


class CiConfig(DevConfig):
    TESTING = True


class ProdConfig(Config):
    pass


class ContinuumTestConfig(ProdConfig):
    pass


class End2EndConfig(ProdConfig):
    pass


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
