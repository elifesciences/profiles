from unittest.mock import MagicMock, patch

from flask.testing import FlaskClient
import pytest
from requests import RequestException
import requests_mock
from werkzeug.exceptions import Forbidden

from profiles.database import db
from profiles.exceptions import OrcidTokenNotFound
from profiles.models import Name, OrcidToken, Profile
from profiles.repositories import SQLAlchemyOrcidTokens
from profiles.utilities import expires_at


def test_it_updates_and_returns_204_if_a_profile_is_found(test_client: FlaskClient) -> None:
    profile = Profile('a1b2c3d4', Name('Foo Bar'), '0000-0002-1825-0097')
    orcid_token = OrcidToken('0000-0002-1825-0097', 'access-token', expires_at(1234))

    db.session.add(profile)
    db.session.add(orcid_token)

    with patch('profiles.orcid.request'):
        db.session.commit()

    with requests_mock.Mocker() as mocker:
        mocker.get('http://www.example.com/api/v2.0/0000-0002-1825-0097/record',
                   json={'person': {
                       'name': {'family-name': {'value': 'Family Name'},
                                'given-names': {'value': 'Given Names'}}
                   }})

        response = test_client.post('/orcid-webhook/0000-0002-1825-0097')

    assert response.status_code == 204
    assert profile.name.preferred == 'Given Names Family Name'


def test_it_returns_404_if_a_profile_is_not_found(test_client: FlaskClient) -> None:
    response = test_client.post('/orcid-webhook/foo')

    assert response.status_code == 404
    assert response.headers.get('Content-Type') == 'application/problem+json'


def test_it_has_to_be_a_post(test_client: FlaskClient) -> None:
    response = test_client.get('/orcid-webhook/foo')

    assert response.status_code == 405
    assert response.headers.get('Content-Type') == 'application/problem+json'


def test_it_returns_403_if_an_access_token_is_rejected(profile: Profile,
                                                       orcid_token: OrcidToken,
                                                       test_client: FlaskClient) -> None:
    db.session.add(profile)
    db.session.add(orcid_token)

    with patch('profiles.orcid.request'):
        db.session.commit()

    with requests_mock.Mocker() as mocker:
        mocker.get('http://www.example.com/api/v2.0/0001-0002-1825-0097/record', exc=Forbidden)

        response = test_client.post('/orcid-webhook/0001-0002-1825-0097')

    assert response.status_code == 403
    assert response.headers.get('Content-Type') == 'application/problem+json'


def test_it_still_updates_if_public_data_token_has_to_be_used(profile: Profile,
                                                              public_token_resp_data: dict,
                                                              test_client: FlaskClient) -> None:
    db.session.add(profile)

    with patch('profiles.orcid.request'):
        db.session.commit()

    response_data = public_token_resp_data

    with requests_mock.Mocker() as mocker:
        mocker.post('http://www.example.com/oauth/token', json=response_data)

        mocker.get('http://www.example.com/api/v2.0/0001-0002-1825-0097/record',
                   json={'person': {
                       'name': {'family-name': {'value': 'Family Name'},
                                'given-names': {'value': 'Given Names'}}
                   }})

        response = test_client.post('/orcid-webhook/0001-0002-1825-0097')

    assert response.status_code == 204
    assert profile.name.preferred == 'Given Names Family Name'


def test_it_removes_token_if_403_and_public_is_false(profile: Profile,
                                                     test_client: FlaskClient,
                                                     orcid_token: OrcidToken,
                                                     orcid_tokens: SQLAlchemyOrcidTokens) -> None:
    db.session.add(profile)
    db.session.add(orcid_token)

    with patch('profiles.orcid.request'):
        db.session.commit()

    err_response = MagicMock(status_code=403)

    with requests_mock.Mocker() as mocker:
        mocker.get('http://www.example.com/api/v2.0/0001-0002-1825-0097/record',
                   exc=RequestException(response=err_response))

        test_client.post('/orcid-webhook/0001-0002-1825-0097')

    with pytest.raises(OrcidTokenNotFound):
        orcid_tokens.get('0001-0002-1825-0097')
