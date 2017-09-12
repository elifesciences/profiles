import configparser
import json

from flask_script import Manager, Server, Shell

from profiles.config import create_config
from profiles.factory import create_app
from profiles.models import Client, Clients

config = configparser.ConfigParser()
config.read('app.cfg')

clients_json = json.load(open('clients.json'))
clients = Clients([Client(name, **clients_json[name]) for name in clients_json])

app = create_app(create_config(config), clients)
manager = Manager(app)


def make_shell_context() -> dict:
    return {'app': app}


manager.add_command('runserver', Server())
manager.add_command('shell', Shell(make_context=make_shell_context))

if __name__ == '__main__':
    manager.run()
