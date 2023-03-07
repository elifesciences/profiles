import configparser
import logging
import os
import yaml
from profiles.clients import Client, Clients
import profiles.logging
import profiles.config
import profiles.factory

# what is this doing?
os.umask(int('002', 8))

CONFIG_FILE = configparser.ConfigParser()
CONFIG_FILE.read('app.cfg')

# ---

CLIENTS_DATA = yaml.load(open('clients.yaml'), Loader=yaml.FullLoader) or {}
# remove deprecated configuration key
for data in CLIENTS_DATA:
    # upgrade deprecated `redirect_uri` to `redirect_uris`
    if 'redirect_uri' in CLIENTS_DATA[data]:
        CLIENTS_DATA[data]['redirect_uris'] = [CLIENTS_DATA[data]['redirect_uri']]
        del CLIENTS_DATA[data]['redirect_uri']
CLIENTS = Clients(*[Client(name, **CLIENTS_DATA[name]) for name in CLIENTS_DATA])

# ---

CONFIG = profiles.config.create_app_config(CONFIG_FILE)
profiles.logging.configure_logging(env=CONFIG.name,
                                   level=getattr(logging, CONFIG.logging.get('level')),
                                   path=CONFIG.logging.get('path'))

APP = profiles.factory.create_app(CONFIG, CLIENTS)

# two entry points here:
# 1. `manage.APP` used by wsgi
# 2. `python manage.py`, used by humans



'''
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
'''

def runserver():
    pass
