from configparser import RawConfigParser
from typing import Dict


class Config(object):
    def __init__(self, orcid: Dict[str, str]) -> None:
        self.orcid = orcid


class DevConfig(Config):
    DEBUG = True


class CiConfig(DevConfig):
    TESTING = True


class ProdConfig(Config):
    pass


class End2EndConfig(ProdConfig):
    pass


ENVIRONMENTS = {
    'dev': DevConfig,
    'ci': CiConfig,
    'prod': ProdConfig,
    'end2end': End2EndConfig,
}


def create_app_config(config: RawConfigParser) -> Config:
    environment = config.get('profiles', 'environment', fallback='dev')

    arguments = {section: dict(config.items(section)) for section in config.sections()}
    arguments.pop('profiles', None)

    return ENVIRONMENTS[environment](arguments)
