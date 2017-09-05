from flask import Blueprint, make_response
from werkzeug.wrappers import Response

PING_BP = Blueprint('ping', __name__)


@PING_BP.route('/ping')
def ping() -> Response:
    response = make_response('pong')
    response.headers['Content-Type'] = 'text/plain; charset=UTF-8'
    response.headers['Cache-Control'] = 'must-revalidate, no-cache, no-store, private'

    return response
