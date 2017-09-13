import configparser

from flask_script import Manager, Server, Shell
import yaml

from profiles.config import create_config
from profiles.factory import create_app
from profiles.models import Client, Clients

config = configparser.ConfigParser()
config.read('app.cfg')

clients_data = yaml.load(open('clients.yaml'))
clients = Clients([Client(name, **clients_data[name]) for name in clients_data])

app = create_app(create_config(config), clients)
manager = Manager(app)


def make_shell_context() -> dict:
    return {'app': app}


manager.add_command('runserver', Server())
manager.add_command('shell', Shell(make_context=make_shell_context))

if __name__ == '__main__':
    manager.run()
