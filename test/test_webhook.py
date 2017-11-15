from flask.testing import FlaskClient
import requests_mock

from profiles.database import db
from profiles.models import Name, OrcidToken, Profile
from profiles.utilities import expires_at


def test_it_updates_and_returns_204_if_a_profile_is_found(test_client: FlaskClient) -> None:
    profile = Profile('a1b2c3d4', Name('Foo Bar'), '0000-0002-1825-0097')
    orcid_token = OrcidToken('0000-0002-1825-0097', 'access-token', expires_at(1234))

    db.session.add(profile)
    db.session.add(orcid_token)
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
