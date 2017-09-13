from urllib.parse import urlencode

from flask import jsonify, make_response, redirect, request
from werkzeug.exceptions import HTTPException, InternalServerError
from werkzeug.wrappers import Response

from profiles.exceptions import ClientError, OAuth2Error
from profiles.utilities import remove_none_values


def error_handler(exception: Exception) -> Response:
    http_exception = InternalServerError(str(exception))
    http_exception.__cause__ = exception

    return http_error_handler(http_exception)


def client_error_handler(exception: ClientError) -> Response:
    query = remove_none_values({
        'error': exception.error,
        'error_description': exception.description,
    })

    return redirect('{}?{}'.format(exception.uri, urlencode(query)), exception.status_code)


def http_error_handler(exception: HTTPException) -> Response:
    if request.path.startswith('/oauth2/authorize') or request.path.startswith('/oauth2/check'):
        return make_response(exception, exception.code)

    body = {
        'title': getattr(exception, 'description', exception.name),
    }
    response = make_response(jsonify(body), exception.code)
    response.headers['Content-Type'] = 'application/problem+json'

    return response


def oauth2_error_handler(exception: OAuth2Error) -> Response:
    body = remove_none_values({
        'error': exception.error,
        'error_description': exception.description,
    })

    return make_response(jsonify(body), exception.status_code)
