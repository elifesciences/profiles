from http.client import responses
from flask import Flask, jsonify, make_response
from profiles.api.ping import PING_BP
from werkzeug.exceptions import HTTPException, InternalServerError


def create_app():
    app = Flask(__name__)
    app.TRAP_HTTP_EXCEPTIONS = True

    app.register_blueprint(PING_BP)

    def http_error_handler(exception):
        if not isinstance(exception, HTTPException):
            exception = InternalServerError(getattr(exception, 'message', None))

        body = {
            'title': getattr(exception, 'message', responses[exception.code]),
        }
        response = make_response(jsonify(body), exception.code)
        response.headers['Content-Type'] = 'application/problem+json'

        return response

    from werkzeug.exceptions import default_exceptions
    for code in default_exceptions:
        app.errorhandler(code)(http_error_handler)

    return app
