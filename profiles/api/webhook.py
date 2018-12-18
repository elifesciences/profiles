import logging
from typing import Dict

from flask import Blueprint
from itsdangerous import BadSignature, URLSafeSerializer
from requests import RequestException
from werkzeug.exceptions import InternalServerError, NotFound, ServiceUnavailable
from werkzeug.wrappers import Response

from profiles.commands import update_profile_from_orcid_record
from profiles.exceptions import OrcidTokenNotFound, ProfileNotFound
from profiles.orcid import OrcidClient
from profiles.repositories import OrcidTokens, Profiles

LOGGER = logging.getLogger()

def create_blueprint(profiles: Profiles, orcid_config: Dict[str, str],
                     orcid_client: OrcidClient, orcid_tokens: OrcidTokens,
                     uri_signer: URLSafeSerializer) -> Blueprint:
    blueprint = Blueprint('webhook', __name__)

    @blueprint.route('/orcid-webhook/<payload>', methods=['POST'])
    def _update(payload: str) -> Response:
        LOGGER.info(msg='POST request made to /orcid-webhook/%s' % payload)

        try:
            orcid = uri_signer.loads(payload)
        except BadSignature as exception:
            LOGGER.error(msg='Bad signature error for /orcid-webhook/%s' % payload)
            raise NotFound from exception

        try:
            profile = profiles.get_by_orcid(orcid)
        except ProfileNotFound as exception:
            raise NotFound(str(exception)) from exception

        try:
            access_token = orcid_tokens.get(profile.orcid).access_token
        except OrcidTokenNotFound:
            LOGGER.info(msg='Access Token not found for %s. Reverting to public '
                            'access token' % profile.orcid)
            access_token = orcid_config.get('read_public_access_token')

        try:
            orcid_record = orcid_client.get_record(orcid, access_token)
        except RequestException as exception:
            if exception.response.status_code == 403 and not access_token == \
                    orcid_config.get('read_public_access_token'):
                orcid_tokens.remove(profile.orcid)

                # Let ORCID retry, it will use the public access token
                raise ServiceUnavailable from exception

            raise InternalServerError from exception

        update_profile_from_orcid_record(profile, orcid_record)

        return Response(status=204)

    return blueprint
