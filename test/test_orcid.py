import pytest
from requests import HTTPError
import requests_mock

from profiles.orcid import OrcidClient


def test_it_gets_a_record():
    orcid_client = OrcidClient('http://www.example.com/api')

    with requests_mock.Mocker() as mocker:
        mocker.get('http://www.example.com/api/v2.1/0000-0002-1825-0097/record',
                   request_headers={'Accept': 'application/orcid+json',
                                    'Authorization': 'Bearer 1/fFAGRNJru1FTz70BzhT3Zg'},
                   json={'foo': 'bar'})

        record = orcid_client.get_record('0000-0002-1825-0097', '1/fFAGRNJru1FTz70BzhT3Zg')

    assert record == {'foo': 'bar'}


def test_it_raises_http_errors():
    orcid_client = OrcidClient('http://www.example.com/api')

    with requests_mock.Mocker() as mocker, pytest.raises(HTTPError):
        mocker.get('http://www.example.com/api/v2.1/0000-0002-1825-0097/record', status_code=404)

        orcid_client.get_record('0000-0002-1825-0097', '1/fFAGRNJru1FTz70BzhT3Zg')
