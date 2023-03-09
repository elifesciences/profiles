import re
import sys
from configparser import RawConfigParser
from typing import Dict


class Config():
    name = 'unknown'
    DEBUG = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    TESTING = False

    # pylint: disable=invalid-name,too-many-arguments
    def __init__(self, orcid: Dict[str, str], db: str, logging: Dict[str, str],
                 bus: Dict[str, str], scheme: str, server_name: str = None, **_kwargs) -> None:
        self.orcid = orcid
        self.SQLALCHEMY_DATABASE_URI = db
        self.logging = logging
        self.bus = bus
        self.SERVER_NAME = server_name
        self.PREFERRED_URL_SCHEME = scheme

    def db_host(self):
        m = re.match('.*@(.*)/.*', self.SQLALCHEMY_DATABASE_URI)
        if m:
            return m.group(1)
        else:
            raise RuntimeError

    def web_host(self):
        return self.SERVER_NAME


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


def all_config_classes_by_name():
    current_module = sys.modules[__name__]
    config_classes = [getattr(current_module, entity) for entity in current_module.__dict__ if
                      re.match('^.+Config$', entity)]
    return {class_.__dict__['name']: class_ for class_ in config_classes}


ENVIRONMENTS = all_config_classes_by_name()


def create_app_config(config: RawConfigParser) -> Config:
    kwargs = {section: dict(config.items(section)) for section in config.sections()}
    kwargs = {**kwargs.pop('profiles', {}), **kwargs}
    environment = kwargs.pop('environment', 'dev')

    return ENVIRONMENTS[environment](**kwargs)
