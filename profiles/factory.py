import hashlib

from elife_bus_sdk import get_publisher
from flask import Flask
from flask_sqlalchemy import models_committed
from itsdangerous import URLSafeSerializer

from profiles.api import api, errors, oauth2, ping, webhook
from profiles.clients import Clients
from profiles.config import Config
from profiles.events import maintain_orcid_webhook, send_update_events
from profiles.exceptions import ClientError, OAuth2Error
from profiles.database import db, migrate
from profiles.orcid import OrcidClient
from profiles.repositories import SQLAlchemyOrcidTokens, SQLAlchemyProfiles


def create_app(config: Config, clients: Clients) -> Flask:
    app = Flask(__name__)
    app.TRAP_HTTP_EXCEPTIONS = True
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)

    orcid_client = OrcidClient(config.orcid['api_uri'])
    app.orcid_client = orcid_client

    app.orcid_tokens = SQLAlchemyOrcidTokens(db)
    app.profiles = SQLAlchemyProfiles(db)

    app.uri_signer = URLSafeSerializer(config.orcid['webhook_key'],
                                   signer_kwargs={'key_derivation': 'hmac',
                                                  'digest_method': hashlib.sha512})

    config_bus = dict(config.bus)
    config_bus['env'] = config.name
    publisher = get_publisher(config=config_bus)
    app.register_blueprint(api.create_blueprint(app.profiles))
    app.register_blueprint(oauth2.create_blueprint(config.orcid, clients, app.profiles, app.orcid_client,
                                                   app.orcid_tokens), url_prefix='/oauth2')
    app.register_blueprint(ping.create_blueprint())
    app.register_blueprint(webhook.create_blueprint(app.profiles, config.orcid, app.orcid_client,
                                                    app.orcid_tokens, app.uri_signer))

    from werkzeug.exceptions import default_exceptions
    for code in default_exceptions:
        app.errorhandler(code)(errors.http_error_handler)

    app.register_error_handler(Exception, errors.error_handler)
    app.register_error_handler(ClientError, errors.client_error_handler)
    app.register_error_handler(OAuth2Error, errors.oauth2_error_handler)

    models_committed.connect(maintain_orcid_webhook(config.orcid, orcid_client, app.uri_signer),
                             weak=False)
    models_committed.connect(send_update_events(publisher=publisher), weak=False)

    return app
