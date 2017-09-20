from flask import Flask
from flask_migrate import Migrate
from werkzeug.contrib.fixers import ProxyFix

from profiles.api import errors, oauth2, ping
from profiles.clients import Clients
from profiles.config import Config
from profiles.exceptions import ClientError, OAuth2Error
from profiles.models import db
from profiles.repositories import SQLAlchemyOrcidTokens, SQLAlchemyProfiles


def create_app(config: Config, clients: Clients) -> Flask:
    app = Flask(__name__)
    app.TRAP_HTTP_EXCEPTIONS = True
    app.config.from_object(config)

    app.wsgi_app = ProxyFix(app.wsgi_app)

    db.app = app
    db.init_app(app)

    Migrate(app, db)

    orcid_tokens = SQLAlchemyOrcidTokens(db)
    profiles = SQLAlchemyProfiles(db)

    app.register_blueprint(oauth2.create_blueprint(config.orcid, clients, profiles, orcid_tokens),
                           url_prefix='/oauth2')
    app.register_blueprint(ping.create_blueprint())

    from werkzeug.exceptions import default_exceptions
    for code in default_exceptions:
        app.errorhandler(code)(errors.http_error_handler)

    app.register_error_handler(Exception, errors.error_handler)
    app.register_error_handler(ClientError, errors.client_error_handler)
    app.register_error_handler(OAuth2Error, errors.oauth2_error_handler)

    return app
