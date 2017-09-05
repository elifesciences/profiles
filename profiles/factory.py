from urllib.parse import urlencode

from flask import Flask, jsonify, make_response, redirect, request
from profiles.api.errors import OAuth2Error, ClientError
from profiles.api.oauth2 import OAUTH2_BP
from profiles.api.ping import PING_BP
from profiles.utilities import remove_none_values
from werkzeug.exceptions import HTTPException, InternalServerError


def create_app(config: dict):
    app = Flask(__name__)
    app.TRAP_HTTP_EXCEPTIONS = True
    app.config.update(dict(
        config=config
    ))

    app.register_blueprint(OAUTH2_BP, url_prefix='/oauth2')
    app.register_blueprint(PING_BP)

    def http_error_handler(exception):
        if isinstance(exception, ClientError):
            return redirect(exception.uri + '?' + urlencode(remove_none_values({
                'error': exception.error,
                'error_description': exception.description,
            })), exception.status_code)

        if isinstance(exception, OAuth2Error):
            body = remove_none_values({
                'error': exception.error,
                'error_description': exception.description,
            })
            return make_response(jsonify(body), exception.status_code)

        if not isinstance(exception, HTTPException):
            exception = InternalServerError(getattr(exception, 'message', None))

        if request.path.startswith('/oauth2/authorize') or request.path.startswith('/oauth2/check'):
            return make_response(exception, exception.code)

        body = {
            'title': getattr(exception, 'description', exception.name),
        }
        response = make_response(jsonify(body), exception.code)
        response.headers['Content-Type'] = 'application/problem+json'

        return response

    from werkzeug.exceptions import default_exceptions
    for code in default_exceptions:
        app.errorhandler(code)(http_error_handler)

    return app
