import json
import logging
from urllib.parse import quote
from urllib3.util.retry import Retry
import requests

API_VERSION = 'v2.1'
LOGGER = logging.getLogger(__name__)

VISIBILITY_PUBLIC = 'PUBLIC'
VISIBILITY_LIMITED = 'LIMITED'
VISIBILITY_PRIVATE = 'PRIVATE'


class OrcidClient(object):
    def __init__(self, api_uri: str) -> None:
        self.api_uri = api_uri

    def get_record(self, orcid: str, access_token: str) -> dict:
        LOGGER.debug('Requesting ORCID record for %s', format(orcid))

        try:
            response = self._get_request('{}/{}/record'.format(API_VERSION, orcid), access_token)
        except requests.RequestException as exception:
            LOGGER.warning('Failed to load ORCID record for %s (%s)', orcid, str(exception))
            raise exception

        LOGGER.debug('Received ORCID record for %s', orcid)

        return json.loads(response.text)

    def set_webhook(self, orcid: str, webhook: str, access_token: str) -> None:
        LOGGER.debug('Setting ORCID webhook %s for %s', webhook, orcid)

        try:
            self._request('put', '{}/webhook/{}'.format(orcid, quote(webhook, safe='')),
                          access_token)
        except requests.RequestException as exception:
            LOGGER.warning('Failed to set ORCID webhook %s for %s (%s)', webhook, orcid,
                           str(exception))
            raise exception

        LOGGER.debug('Set ORCID webhook %s for %s', webhook, orcid)

    def remove_webhook(self, orcid: str, webhook: str, access_token: str) -> None:
        LOGGER.debug('Removing ORCID webhook %s for %s', webhook, orcid)

        try:
            self._request('delete', '{}/webhook/{}'.format(orcid, quote(webhook, safe='')),
                          access_token)
        except requests.RequestException as exception:
            LOGGER.warning('Failed to set ORCID webhook %s for %s (%s)', webhook, orcid,
                           str(exception))
            raise exception

        LOGGER.debug('Removed ORCID webhook %s for %s', webhook, orcid)

    def _get_request(self, path: str, access_token: str) -> requests.Response:
        headers = {'Accept': 'application/orcid+json',
                   'User-Agent': "profiles/master (https://github.com/elifesciences/profiles)"}

        return self._request('get', path, access_token, headers)

    def _request(self, method: str, path: str, access_token: str, headers: dict = None) -> requests.Response:
        if headers is None:
            headers = {}

        uri = '{}/{}'.format(self.api_uri, path)
        headers['Authorization'] = 'Bearer ' + access_token

        MAX_RETRIES = 3

        # lsh@2023-07-28: handle network errors better.
        # - https://urllib3.readthedocs.io/en/stable/user-guide.html#retrying-requests
        # - https://urllib3.readthedocs.io/en/stable/reference/urllib3.util.html
        max_retries_obj = Retry(**{
            'total': MAX_RETRIES,
            'connect': MAX_RETRIES,
            'read': MAX_RETRIES,
            # "How many times to retry on bad status codes.
            # These are retries made on responses, where status code matches status_forcelist."
            'status': MAX_RETRIES,
            'status_forcelist': [413, 429, 503, # defaults
                                 500, 502, 504],
            # {backoff factor} * (2 ** {number of previous retries})
            # 0.3 => 0.3, 0.6, 1.2, 2.4, 4.8
            'backoff_factor': 0.3,
        })
        adaptor = requests.adapters.HTTPAdapter(max_retries=max_retries_obj)
        session = requests.Session()
        session.mount('https://', adaptor)

        response = session.request(method, uri, headers=headers)
        response.raise_for_status()

        return response
