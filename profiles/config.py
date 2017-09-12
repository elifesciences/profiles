from configparser import RawConfigParser


class Config(object):
    def __init__(self, orcid: dict):
        self.orcid = orcid


class DevConfig(Config):
    DEBUG = True


class CiConfig(DevConfig):
    TESTING = True


class ProdConfig(Config):
    pass


class End2EndConfig(ProdConfig):
    pass


def create_config(config: RawConfigParser) -> Config:
    if config.has_option('profiles', 'environment'):
        environment = config['profiles']['environment']
    else:
        environment = 'dev'

    if environment == 'dev':
        return DevConfig(config['orcid'])
    elif environment == 'ci':
        return CiConfig(config['orcid'])
    if environment == 'prod':
        return ProdConfig(config['orcid'])
    if environment == 'end2end':
        return End2EndConfig(config['orcid'])

    raise KeyError('Unknown environment {}'.format(environment))
