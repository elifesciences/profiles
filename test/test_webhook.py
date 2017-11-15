from flask.testing import FlaskClient

from profiles.database import db
from profiles.models import Name, Profile


def test_it_returns_204_if_a_profile_is_found(test_client: FlaskClient) -> None:
    profile = Profile('a1b2c3d4', Name('Foo Bar'), '0000-0002-1825-0097')

    db.session.add(profile)
    db.session.commit()

    response = test_client.post('/orcid-webhook/0000-0002-1825-0097')

    assert response.status_code == 204


def test_it_returns_404_if_a_profile_is_not_found(test_client: FlaskClient) -> None:
    response = test_client.post('/orcid-webhook/foo')

    assert response.status_code == 404
    assert response.headers.get('Content-Type') == 'application/problem+json'


def test_it_has_to_be_a_post(test_client: FlaskClient) -> None:
    response = test_client.get('/orcid-webhook/foo')

    assert response.status_code == 405
    assert response.headers.get('Content-Type') == 'application/problem+json'
