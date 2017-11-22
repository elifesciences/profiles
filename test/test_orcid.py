import pytest
from requests import HTTPError
from requests.exceptions import RequestException
import requests_mock

from profiles.orcid import OrcidClient


def test_it_gets_a_record(orcid_client: OrcidClient):
    with requests_mock.Mocker() as mocker:
        mocker.get('http://www.example.com/api/v2.0/0000-0002-1825-0097/record',
                   request_headers={'Accept': 'application/orcid+json',
                                    'Authorization': 'Bearer 1/fFAGRNJru1FTz70BzhT3Zg'},
                   json={'foo': 'bar'})

        record = orcid_client.get_record('0000-0002-1825-0097', '1/fFAGRNJru1FTz70BzhT3Zg')

    assert record == {'foo': 'bar'}


def test_it_sets_a_webhook(orcid_client: OrcidClient):
    with requests_mock.Mocker() as mocker:
        mocker.put('http://www.example.com/api/v2.0/0000-0002-1825-0097/webhook/'
                   'http%3A%2F%2Flocalhost%2Forcid-webhook%2F0000-0002-1825-0097',
                   request_headers={'Authorization': 'Bearer 1/fFAGRNJru1FTz70BzhT3Zg'})

        orcid_client.set_webhook('0000-0002-1825-0097',
                                 'http://localhost/orcid-webhook/0000-0002-1825-0097',
                                 '1/fFAGRNJru1FTz70BzhT3Zg')


def test_it_removes_a_webhook(orcid_client: OrcidClient):
    with requests_mock.Mocker() as mocker:
        mocker.delete('http://www.example.com/api/v2.0/0000-0002-1825-0097/webhook/'
                      'http%3A%2F%2Flocalhost%2Forcid-webhook%2F0000-0002-1825-0097',
                      request_headers={'Authorization': 'Bearer 1/fFAGRNJru1FTz70BzhT3Zg'})

        orcid_client.remove_webhook('0000-0002-1825-0097',
                                    'http://localhost/orcid-webhook/0000-0002-1825-0097',
                                    '1/fFAGRNJru1FTz70BzhT3Zg')


def test_it_raises_http_errors(orcid_client: OrcidClient):
    with requests_mock.Mocker() as mocker, pytest.raises(HTTPError):
        mocker.get('http://www.example.com/api/v2.0/0000-0002-1825-0097/record', status_code=404)

        orcid_client.get_record('0000-0002-1825-0097', '1/fFAGRNJru1FTz70BzhT3Zg')


def test_it_can_get_public_data_token(orcid_client: OrcidClient,
                                      public_token_resp_data: dict):
    response_data = public_token_resp_data

    with requests_mock.Mocker() as mocker:
        mocker.post('http://www.example.com/oauth/token', json=response_data)

        token = orcid_client.get_access_token(public_token=True)

    assert token == "4bed1e13-7792-4129-9f07-aaf7b88ba88f"


def test_it_raises_exception_if_public_data_token_request_fails(orcid_client: OrcidClient):
    with requests_mock.Mocker() as mocker:
        mocker.post('http://www.example.com/oauth/token', exc=RequestException)

        with pytest.raises(RequestException):
            orcid_client.get_access_token(public_token=True)
