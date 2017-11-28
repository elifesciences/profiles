from typing import Dict

from flask import Blueprint
from requests import RequestException
from werkzeug.exceptions import NotFound
from werkzeug.wrappers import Response

from profiles.commands import update_profile_from_orcid_record
from profiles.exceptions import OrcidTokenNotFound, ProfileNotFound
from profiles.orcid import OrcidClient
from profiles.repositories import OrcidTokens, Profiles


def create_blueprint(profiles: Profiles, orcid_config: Dict[str, str],
                     orcid_client: OrcidClient, orcid_tokens: OrcidTokens) -> Blueprint:
    blueprint = Blueprint('webhook', __name__)

    @blueprint.route('/orcid-webhook/<orcid>', methods=['POST'])
    def _update(orcid: str) -> Response:
        is_token_public_flag = False

        try:
            profile = profiles.get_by_orcid(orcid)
        except ProfileNotFound as exception:
            raise NotFound(str(exception)) from exception

        try:
            access_token = orcid_tokens.get(profile.orcid).access_token
        except OrcidTokenNotFound:
            access_token = orcid_config.get('read_public_access_token')
            is_token_public_flag = True

        try:
            orcid_record = orcid_client.get_record(orcid, access_token)
        except RequestException as exception:
            if exception.response.status_code == 403 and not is_token_public_flag:
                orcid_tokens.remove(profile.orcid)

            raise exception

        update_profile_from_orcid_record(profile, orcid_record)

        return Response(status=204)

    return blueprint
