from flask import Blueprint
from requests import RequestException
from werkzeug.exceptions import Forbidden, NotFound
from werkzeug.wrappers import Response

from profiles.commands import update_profile_from_orcid_record
from profiles.exceptions import ProfileNotFound
from profiles.orcid import OrcidClient
from profiles.repositories import OrcidTokens, Profiles


def create_blueprint(profiles: Profiles, orcid_client: OrcidClient,
                     orcid_tokens: OrcidTokens) -> Blueprint:
    blueprint = Blueprint('webhook', __name__)

    @blueprint.route('/orcid-webhook/<orcid>', methods=['POST'])
    def _update(orcid: str) -> Response:
        try:
            profile = profiles.get_by_orcid(orcid)
        except ProfileNotFound as exception:
            raise NotFound(str(exception)) from exception

        access_token = orcid_tokens.get(profile.orcid)

        try:
            orcid_record = orcid_client.get_record(orcid, access_token.access_token)
        except RequestException as exception:
            raise Forbidden(str(exception)) from exception

        update_profile_from_orcid_record(profile, orcid_record)

        return Response(status=204)

    return blueprint
