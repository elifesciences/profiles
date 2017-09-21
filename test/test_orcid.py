import pytest
import responses
from requests import HTTPError

from profiles.orcid import OrcidClient


@responses.activate
def test_it_gets_a_record():
    responses.add(responses.GET, 'http://www.example.com/api/v2.0/0000-0002-1825-0097/record',
                  status=200, json={'foo': 'bar'})

    orcid_client = OrcidClient('http://www.example.com/api')

    record = orcid_client.get_record('0000-0002-1825-0097', '1/fFAGRNJru1FTz70BzhT3Zg')

    assert record == {'foo': 'bar'}


@responses.activate
def test_it_raises_http_errors():
    responses.add(responses.GET, 'http://www.example.com/api/v2.0/0000-0002-1825-0097/record',
                  status=404)

    orcid_client = OrcidClient('http://www.example.com/api')

    with pytest.raises(HTTPError):
        orcid_client.get_record('0000-0002-1825-0097', '1/fFAGRNJru1FTz70BzhT3Zg')
