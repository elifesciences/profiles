from flask import Flask

from profiles.api import errors, oauth2, ping
from profiles.config import Config
from profiles.exceptions import ClientError, OAuth2Error
from profiles.models import Clients


def create_app(config: Config, clients: Clients) -> Flask:
    app = Flask(__name__)
    app.TRAP_HTTP_EXCEPTIONS = True
    app.config.from_object(config)

    app.register_blueprint(oauth2.create_blueprint(config.orcid, clients), url_prefix='/oauth2')
    app.register_blueprint(ping.create_blueprint())

    from werkzeug.exceptions import default_exceptions
    for code in default_exceptions:
        app.errorhandler(code)(errors.http_error_handler)

    app.register_error_handler(Exception, errors.error_handler)
    app.register_error_handler(ClientError, errors.client_error_handler)
    app.register_error_handler(OAuth2Error, errors.oauth2_error_handler)

    return app
