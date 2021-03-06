import configparser
import logging
import os

from flask_migrate import MigrateCommand
from flask_script import Manager, Server, Shell
import yaml

from profiles.clients import Client, Clients
from profiles.config import create_app_config
from profiles.factory import create_app
from profiles.logging import configure_logging

os.umask(int('002', 8))

CONFIG_FILE = configparser.ConfigParser()
CONFIG_FILE.read('app.cfg')

CLIENTS_DATA = yaml.load(open('clients.yaml')) or {}
# remove deprecated configuration key
for data in CLIENTS_DATA:
    # upgrade deprecated `redirect_uri` to `redirect_uris`
    if 'redirect_uri' in CLIENTS_DATA[data]:
        CLIENTS_DATA[data]['redirect_uris'] = [CLIENTS_DATA[data]['redirect_uri']]
        del CLIENTS_DATA[data]['redirect_uri']
CLIENTS = Clients(*[Client(name, **CLIENTS_DATA[name]) for name in CLIENTS_DATA])

CONFIG = create_app_config(CONFIG_FILE)
configure_logging(env=CONFIG.name,
                  level=getattr(logging, CONFIG.logging.get('level')),
                  path=CONFIG.logging.get('path'))

APP = create_app(CONFIG, CLIENTS)
MANAGER = Manager(APP)


def make_shell_context() -> dict:
    return {'app': APP}


MANAGER.add_command('db', MigrateCommand)
MANAGER.add_command('runserver', Server())
MANAGER.add_command('shell', Shell(make_context=make_shell_context))

for c in APP.commands:
    MANAGER.add_command(c.NAME, c)

if __name__ == '__main__':
    MANAGER.run()
