import configparser
import logging
import os

import yaml
from flask_migrate import MigrateCommand
from flask_script import Manager, Server, Shell

from profiles.clients import Client, Clients
from profiles.config import create_app_config
from profiles.factory import create_app
from profiles.logging import configure_logging

os.umask(int('002', 8))

config_file = configparser.ConfigParser()
config_file.read('app.cfg')

clients_data = yaml.load(open('clients.yaml')) or {}
clients = Clients(*[Client(name, **clients_data[name]) for name in clients_data])

config = create_app_config(config_file)
configure_logging(config.name, getattr(logging, config.logging['level']), config.logging['path'])
app = create_app(config, clients)
manager = Manager(app)


def make_shell_context() -> dict:
    return {'app': app}


manager.add_command('db', MigrateCommand)
manager.add_command('runserver', Server())
manager.add_command('shell', Shell(make_context=make_shell_context))

if __name__ == '__main__':
    manager.run()
