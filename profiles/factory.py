from elife_bus_sdk import get_publisher
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import models_committed

from profiles.api import api, errors, oauth2, ping, webhook
from profiles.cli import ClearCommand
from profiles.clients import Clients
from profiles.config import Config
from profiles.events import maintain_orcid_webhook, send_update_events
from profiles.exceptions import ClientError, OAuth2Error
from profiles.models import db
from profiles.orcid import OrcidClient
from profiles.repositories import SQLAlchemyOrcidTokens, SQLAlchemyProfiles


def create_app(config: Config, clients: Clients) -> Flask:
    app = Flask(__name__)
    app.TRAP_HTTP_EXCEPTIONS = True
    app.config.from_object(config)

    db.app = app
    db.init_app(app)

    Migrate(app, db)

    orcid_client = OrcidClient(api_uri=config.orcid['api_uri'], token_uri=config.orcid['token_uri'],
                               client_id=config.orcid['client_id'], client_secret=['client_secret'],
                               read_public_access_token=config.orcid['read_public_access_token'],
                               webhook_access_token=config.orcid['webhook_access_token'])
    orcid_tokens = SQLAlchemyOrcidTokens(db)
    profiles = SQLAlchemyProfiles(db)

    publisher = get_publisher(pub_name='profiles', config={'region': config.bus['region'],
                                                           'subscriber': config.bus['subscriber'],
                                                           'name': config.bus['name'],
                                                           'env': config.name})
    app.commands = [ClearCommand(orcid_tokens, profiles)]

    app.register_blueprint(api.create_blueprint(profiles))
    app.register_blueprint(oauth2.create_blueprint(config.orcid, clients, profiles, orcid_client,
                                                   orcid_tokens), url_prefix='/oauth2')
    app.register_blueprint(ping.create_blueprint())
    app.register_blueprint(webhook.create_blueprint(profiles, orcid_client, orcid_tokens))

    from werkzeug.exceptions import default_exceptions
    for code in default_exceptions:
        app.errorhandler(code)(errors.http_error_handler)

    app.register_error_handler(Exception, errors.error_handler)
    app.register_error_handler(ClientError, errors.client_error_handler)
    app.register_error_handler(OAuth2Error, errors.oauth2_error_handler)

    models_committed.connect(maintain_orcid_webhook(orcid_client), weak=False)
    models_committed.connect(send_update_events(publisher=publisher), weak=False)

    return app
