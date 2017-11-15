from flask import Blueprint
from werkzeug.exceptions import NotFound
from werkzeug.wrappers import Response

from profiles.exceptions import ProfileNotFound
from profiles.repositories import Profiles


def create_blueprint(profiles: Profiles) -> Blueprint:
    blueprint = Blueprint('webhook', __name__)

    @blueprint.route('/orcid-webhook/<orcid>', methods=['POST'])
    def _update(orcid: str) -> Response:
        try:
            profiles.get_by_orcid(orcid)
        except ProfileNotFound as exception:
            raise NotFound(str(exception)) from exception

        return Response(status=204)

    return blueprint
