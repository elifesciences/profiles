from flask import Flask

from profiles.api import errors
from profiles.api.oauth2 import OAUTH2_BP
from profiles.api.ping import PING_BP
from profiles.exceptions import ClientError, OAuth2Error


def create_app(config: dict) -> Flask:
    app = Flask(__name__)
    app.TRAP_HTTP_EXCEPTIONS = True
    app.config.update({'config': config})

    app.register_blueprint(OAUTH2_BP, url_prefix='/oauth2')
    app.register_blueprint(PING_BP)

    from werkzeug.exceptions import default_exceptions
    for code in default_exceptions:
        app.errorhandler(code)(errors.http_error_handler)

    app.register_error_handler(Exception, errors.error_handler)
    app.register_error_handler(ClientError, errors.client_error_handler)
    app.register_error_handler(OAuth2Error, errors.oauth2_error_handler)

    return app
