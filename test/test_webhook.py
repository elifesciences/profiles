from typing import Callable

from flask.testing import FlaskClient
import pytest
import requests_mock

from profiles.database import db
from profiles.exceptions import OrcidTokenNotFound
from profiles.models import Name, OrcidToken, Profile
from profiles.repositories import SQLAlchemyOrcidTokens
from profiles.utilities import expires_at


def test_it_updates_and_returns_204_if_a_profile_is_found(test_client: FlaskClient,
                                                          webhook_payload: str,
                                                          commit: Callable[[], None]) -> None:
    profile = Profile('a1b2c3d4', Name('Foo Bar'), '0000-0002-1825-0097')
    orcid_token = OrcidToken('0000-0002-1825-0097', 'access-token', expires_at(1234))

    db.session.add(profile)
    db.session.add(orcid_token)

    commit()

    with requests_mock.Mocker() as mocker:
        mocker.get('http://www.example.com/api/v2.1/0000-0002-1825-0097/record',
                   json={'person': {
                       'name': {'family-name': {'value': 'Family Name'},
                                'given-names': {'value': 'Given Names'}}
                   }})

        response = test_client.post('/orcid-webhook/{}'.format(webhook_payload))

    assert response.status_code == 204
    assert profile.name.preferred == 'Given Names Family Name'


def test_it_returns_404_if_a_payload_is_invalid(test_client: FlaskClient) -> None:
    response = test_client.post('/orcid-webhook/foo')

    assert response.status_code == 404
    assert response.headers.get('Content-Type') == 'application/problem+json'


def test_it_returns_404_if_a_profile_is_not_found(test_client: FlaskClient,
                                                  webhook_payload: str) -> None:
    response = test_client.post('/orcid-webhook/{}'.format(webhook_payload))

    assert response.status_code == 404
    assert response.headers.get('Content-Type') == 'application/problem+json'


def test_it_has_to_be_a_post(test_client: FlaskClient) -> None:
    response = test_client.get('/orcid-webhook/foo')

    assert response.status_code == 405
    assert response.headers.get('Content-Type') == 'application/problem+json'


def test_it_returns_503_if_an_access_token_is_rejected(profile: Profile, orcid_token: OrcidToken,
                                                       test_client: FlaskClient,
                                                       webhook_payload: str,
                                                       commit: Callable[[], None]) -> None:
    db.session.add(profile)
    db.session.add(orcid_token)

    commit()

    with requests_mock.Mocker() as mocker:
        mocker.get('http://www.example.com/api/v2.1/0000-0002-1825-0097/record', status_code=403)

        response = test_client.post('/orcid-webhook/{}'.format(webhook_payload))

    assert response.status_code == 503
    assert response.headers.get('Content-Type') == 'application/problem+json'


# pylint: disable=too-many-arguments
def test_it_removes_token_if_it_was_rejected(profile: Profile, test_client: FlaskClient,
                                             orcid_token: OrcidToken,
                                             orcid_tokens: SQLAlchemyOrcidTokens,
                                             webhook_payload: str,
                                             commit: Callable[[], None]) -> None:
    db.session.add(profile)
    db.session.add(orcid_token)

    commit()

    with requests_mock.Mocker() as mocker:
        mocker.get('http://www.example.com/api/v2.1/0000-0002-1825-0097/record', status_code=403)

        test_client.post('/orcid-webhook/{}'.format(webhook_payload))

    with pytest.raises(OrcidTokenNotFound):
        orcid_tokens.get('0000-0002-1825-0097')


def test_it_returns_500_on_an_orcid_error(profile: Profile, orcid_token: OrcidToken,
                                          test_client: FlaskClient, webhook_payload: str,
                                          commit: Callable[[], None]) -> None:
    db.session.add(profile)
    db.session.add(orcid_token)

    commit()

    with requests_mock.Mocker() as mocker:
        mocker.get('http://www.example.com/api/v2.1/0000-0002-1825-0097/record', status_code=404)

        response = test_client.post('/orcid-webhook/{}'.format(webhook_payload))

    assert response.status_code == 500
    assert response.headers.get('Content-Type') == 'application/problem+json'
