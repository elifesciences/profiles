from flask import Flask, jsonify, make_response
from profiles.api.ping import PING_BP
from werkzeug.exceptions import HTTPException, InternalServerError
from werkzeug.wrappers import Response


def create_app():
    app = Flask(__name__)
    app.TRAP_HTTP_EXCEPTIONS = True

    app.register_blueprint(PING_BP)

    def http_error_handler(exception: Exception) -> Response:
        if not isinstance(exception, HTTPException):
            exception = InternalServerError(str(exception))

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
