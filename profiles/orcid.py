import json
import logging

import requests
from requests import Response, RequestException

API_VERSION = 'v2.0'
LOGGER = logging.getLogger(__name__)


class OrcidClient(object):
    def __init__(self, api_uri: str) -> None:
        self.api_uri = api_uri

    def get_record(self, orcid: str, access_token: str) -> dict:
        LOGGER.debug('Requesting ORCID record for {}'.format(orcid))

        try:
            response = self._get_request('{}/record'.format(orcid), access_token)
        except RequestException as exception:
            LOGGER.warning('Failed to load ORCID record for {} ({})'.format(orcid, str(exception)))
            raise exception

        LOGGER.debug('Received ORCID record for {}'.format(orcid))

        return json.loads(response.text)

    def _get_request(self, path, access_token) -> Response:
        uri = '{}/{}/{}'.format(self.api_uri, API_VERSION, path)
        headers = {'Accept': 'application/orcid+json', 'Authorization': 'Bearer ' + access_token}

        response = requests.get(uri, headers=headers)
        response.raise_for_status()

        return response
