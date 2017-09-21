import json

import requests
from requests import Response

API_VERSION = 'v2.0'


class OrcidClient(object):
    def __init__(self, api_uri: str) -> None:
        self.api_uri = api_uri

    def get_record(self, orcid: str, access_token: str) -> dict:
        response = self._get_request('{}/record'.format(orcid), access_token)

        return json.loads(response.text)

    def _get_request(self, path, access_token) -> Response:
        uri = '{}/{}/{}'.format(self.api_uri, API_VERSION, path)
        headers = {'Accept': 'application/orcid+json', 'Authorization': 'Bearer ' + access_token}

        response = requests.get(uri, headers=headers)
        response.raise_for_status()

        return response
