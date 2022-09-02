from flask import Blueprint, make_response
from werkzeug.wrappers import Response

from profiles.utilities import no_cache


def create_blueprint() -> Blueprint:
    blueprint = Blueprint("ping", __name__)

    @blueprint.route("/ping")
    @no_cache
    def _ping() -> Response:
        response = make_response("pong")
        response.headers["Content-Type"] = "text/plain; charset=UTF-8"

        return response

    @blueprint.route("/error")
    def _error() -> Response:
        raise RuntimeError("Intentional error")

    return blueprint
