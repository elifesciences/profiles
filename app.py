'''
flask app instance and command line wrangling is spread across several files.

./app.py (this) is responsible for loading config and creating a flask app instance called APP.
./manage.py (previous this code) is responsible for wrapping the 'flask' callable.
./profiles/cli.py for command logic, separate from any 'click' magic.
./profiles/factory.py provides the 'create_app' function that will return a configured flask app.

entry points into app.py:
1. `app.APP` used by wsgi, see `config/uwsgi.ini`
2. `python manage.py`, used as CLI
'''
import click
import configparser
import logging
import os
import yaml
from profiles.clients import Client, Clients
import profiles.logging
import profiles.config
import profiles.factory
import profiles.cli

# lsh@2023-03-10: what is this doing? what files is profiles creating?
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

@APP.cli.command("clear")
def clear_command():
    return profiles.cli.ClearCommand(APP.orcid_tokens, APP.profiles)

@APP.cli.command("read-configuration")
@click.option('-s', '--method', 'method', type=str)
def read_configuration_command(method):
    return profiles.cli.ReadConfiguration(CONFIG, method)

@APP.cli.command("create-profile")
@click.option('-e', '--email', 'email', type=str)
@click.option('-n', '--name', 'name', type=str)
def create_profile_command(name, email):
    return profiles.cli.CreateProfileCommand(APP.profiles, name, email)

@APP.cli.command("set-orcid-webhooks")
def set_orcid_webhooks_command():
    return profiles.cli.SetOrcidWebhooksCommand(APP.profiles, CONFIG.orcid, APP.orcid_client, APP.uri_signer)

@APP.cli.command("prune-blocked")
def prune_blocked():
    return profiles.cli.prune_blocked(APP.profiles, APP.orcid_tokens, CONFIG.orcid, APP.orcid_client, APP.uri_signer)

if __name__ == '__main__':
    # lsh@2023-03-07: manage.py became app.py and manage.py now calls flask with some extra command line args.
    # flask.main can't be called from here because then everything gets initialised twice,
    # for example, double logging, double migrations, etc.
    exit(1)
