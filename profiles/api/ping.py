from flask import Blueprint, make_response
from werkzeug.wrappers import Response


def create_blueprint() -> Blueprint:
    blueprint = Blueprint('ping', __name__)

    @blueprint.route('/ping')
    def _ping() -> Response:
        response = make_response('pong')
        response.headers['Content-Type'] = 'text/plain; charset=UTF-8'
        response.headers['Cache-Control'] = 'must-revalidate, no-cache, no-store, private'

        return response

    return blueprint
