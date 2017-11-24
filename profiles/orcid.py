import json
import logging
from urllib.parse import quote

from requests import RequestException, Response, post, request

API_VERSION = 'v2.0'
LOGGER = logging.getLogger(__name__)

WEBHOOK_SCOPE = '/webhook'
READ_PUBLIC_SCOPE = '/read-public'

VISIBILITY_PUBLIC = 'PUBLIC'
VISIBILITY_LIMITED = 'LIMITED'
VISIBILITY_PRIVATE = 'PRIVATE'


class OrcidClient(object):
    def __init__(self, api_uri: str, token_uri: str, client_id: str, client_secret: str) -> None:
        self.api_uri = api_uri
        self.token_uri = token_uri
        self.client_id = client_id
        self.client_secret = client_secret

    def get_access_token(self, public_token: bool = False) -> str:
        LOGGER.debug('Requesting ORCID access token')

        if public_token:
            scope = READ_PUBLIC_SCOPE
        else:
            scope = WEBHOOK_SCOPE

        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': scope,
            'grant_type': 'client_credentials',
        }

        try:
            response = post(url=self.token_uri, data=data, headers={'Accept': 'application/json'})
        except RequestException as exception:
            LOGGER.warning('Failed to obtain ORCID access token (%s)', str(exception))
            raise exception

        LOGGER.debug('Received ORCID public data token')
        json_data = response.json()

        return json_data.get('access_token', '')

    def get_record(self, orcid: str, access_token: str) -> dict:
        LOGGER.debug('Requesting ORCID record for %s', format(orcid))

        try:
            response = self._get_request('{}/record'.format(orcid), access_token)
        except RequestException as exception:
            LOGGER.warning('Failed to load ORCID record for %s (%s)', orcid, str(exception))
            raise exception

        LOGGER.debug('Received ORCID record for %s', orcid)

        return json.loads(response.text)

    def set_webhook(self, orcid: str, webhook: str, access_token: str) -> None:
        LOGGER.debug('Setting ORCID webhook %s for %s', webhook, orcid)

        try:
            self._request('put', '{}/webhook/{}'.format(orcid, quote(webhook, safe='')),
                          access_token)
        except RequestException as exception:
            LOGGER.warning('Failed to set ORCID webhook %s for %s (%s)', webhook, orcid,
                           str(exception))
            raise exception

        LOGGER.debug('Set ORCID webhook %s for %s', webhook, orcid)

    def remove_webhook(self, orcid: str, webhook: str, access_token: str) -> None:
        LOGGER.debug('Removing ORCID webhook %s for %s', webhook, orcid)

        try:
            self._request('delete', '{}/webhook/{}'.format(orcid, quote(webhook, safe='')),
                          access_token)
        except RequestException as exception:
            LOGGER.warning('Failed to set ORCID webhook %s for %s (%s)', webhook, orcid,
                           str(exception))
            raise exception

        LOGGER.debug('Removed ORCID webhook %s for %s', webhook, orcid)

    def _get_request(self, path: str, access_token: str) -> Response:
        headers = {'Accept': 'application/orcid+json'}

        return self._request('get', path, access_token, headers)

    def _request(self, method: str, path: str, access_token: str, headers: dict = None) -> Response:
        if headers is None:
            headers = {}

        uri = '{}/{}/{}'.format(self.api_uri, API_VERSION, path)
        headers['Authorization'] = 'Bearer ' + access_token

        response = request(method, uri, headers=headers)
        response.raise_for_status()

        return response
