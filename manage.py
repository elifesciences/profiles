import configparser

from flask_script import Manager, Server, Shell
import yaml

from profiles.config import create_app_config
from profiles.factory import create_app
from profiles.models import Client, Clients

config_file = configparser.ConfigParser()
config_file.read('app.cfg')

clients_data = yaml.load(open('clients.yaml')) or {}
clients = Clients([Client(name, **clients_data[name]) for name in clients_data])

app = create_app(create_app_config(config_file), clients)
manager = Manager(app)


def make_shell_context() -> dict:
    return {'app': app}


manager.add_command('runserver', Server())
manager.add_command('shell', Shell(make_context=make_shell_context))

if __name__ == '__main__':
    manager.run()
