import logging
from urllib.parse import urlencode

from flask import jsonify, make_response, redirect, request
from werkzeug.exceptions import HTTPException, InternalServerError
from werkzeug.wrappers import Response

from profiles.exceptions import ClientError, OAuth2Error
from profiles.utilities import remove_none_values

LOGGER = logging.getLogger(__name__)

def error_handler(exception: Exception) -> Response:
    LOGGER.exception(exception)

    http_exception = InternalServerError(str(exception))
    http_exception.__cause__ = exception

    return _handle_error(http_exception)


def client_error_handler(exception: ClientError) -> Response:
    LOGGER.exception(exception)

    query = remove_none_values({
        'error': exception.error,
        'error_description': exception.description,
    })

    return redirect('{}?{}'.format(exception.uri, urlencode(query, True)), exception.status_code)


def http_error_handler(exception: HTTPException) -> Response:
    LOGGER.exception(exception)

    return _handle_error(exception)


def oauth2_error_handler(exception: OAuth2Error) -> Response:
    LOGGER.exception(exception)

    body = remove_none_values({
        'error': exception.error,
        'error_description': exception.description,
    })

    return make_response(jsonify(body), exception.status_code)


def _handle_error(exception: HTTPException) -> Response:
    if request.path.startswith('/oauth2/authorize') or request.path.startswith('/oauth2/check'):
        return make_response(exception, exception.code)

    body = {
        'title': getattr(exception, 'description', exception.name),
    }
    response = make_response(jsonify(body), exception.code)
    response.headers['Content-Type'] = 'application/problem+json'

    return response
