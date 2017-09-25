import json

from flask.testing import FlaskClient

from profiles.models import Profile, db


def test_empty_list_of_profile(test_client: FlaskClient) -> None:
    response = test_client.get('/profiles')

    assert response.status_code == 200
    assert response.headers.get(
        'Content-Type') == 'application/vnd.elife.profile-list+json;version=1'

    data = json.loads(response.data.decode('UTF-8'))

    assert data['total'] == 0
    assert len(data['items']) == 0


def test_list_of_profiles(test_client: FlaskClient) -> None:
    for x in range(1, 31):
        db.session.add(Profile(str(x), 'Profile %s' % x))
    db.session.commit()

    response = test_client.get('/profiles')

    assert response.status_code == 200
    assert response.headers.get(
        'Content-Type') == 'application/vnd.elife.profile-list+json;version=1'

    data = json.loads(response.data.decode('UTF-8'))

    assert data['total'] == 30
    assert len(data['items']) == 20
    for x in range(1, 21):
        assert data['items'][x - 1]['id'] == str(x)


def test_list_of_profiles_in_pages(test_client: FlaskClient) -> None:
    for x in range(1, 11):
        db.session.add(Profile(str(x), 'Profile %s' % x))
    db.session.commit()

    response = test_client.get('/profiles?page=1&per-page=5')

    assert response.status_code == 200
    assert response.headers.get(
        'Content-Type') == 'application/vnd.elife.profile-list+json;version=1'

    data = json.loads(response.data.decode('UTF-8'))

    assert data['total'] == 10
    assert len(data['items']) == 5
    for x in range(1, 6):
        assert data['items'][x - 1]['id'] == str(x)

    response = test_client.get('/profiles?page=2&per-page=5')

    assert response.status_code == 200
    assert response.headers.get(
        'Content-Type') == 'application/vnd.elife.profile-list+json;version=1'

    data = json.loads(response.data.decode('UTF-8'))

    assert data['total'] == 10
    assert len(data['items']) == 5
    for x in range(1, 6):
        assert data['items'][x - 1]['id'] == str(x + 5)


def test_404s_on_non_existent_page(test_client: FlaskClient) -> None:
    response = test_client.get('/profiles?page=2')

    assert response.status_code == 404
    assert response.headers.get('Content-Type') == 'application/problem+json'


def test_400s_on_non_integer_page(test_client: FlaskClient) -> None:
    response = test_client.get('/profiles?page=foo')

    assert response.status_code == 400
    assert response.headers.get('Content-Type') == 'application/problem+json'


def test_400s_on_page_less_than_1(test_client: FlaskClient) -> None:
    response = test_client.get('/profiles?page=0')

    assert response.status_code == 400
    assert response.headers.get('Content-Type') == 'application/problem+json'


def test_400s_on_non_integer_per_page(test_client: FlaskClient) -> None:
    response = test_client.get('/profiles?per-page=foo')

    assert response.status_code == 400
    assert response.headers.get('Content-Type') == 'application/problem+json'


def test_400s_on_per_page_less_than_1(test_client: FlaskClient) -> None:
    response = test_client.get('/profiles?per-page=0')

    assert response.status_code == 400
    assert response.headers.get('Content-Type') == 'application/problem+json'


def test_400s_on_per_page_greater_than_100(test_client: FlaskClient) -> None:
    response = test_client.get('/profiles?per-page=101')

    assert response.status_code == 400
    assert response.headers.get('Content-Type') == 'application/problem+json'


def test_get_profile(test_client: FlaskClient) -> None:
    profile = Profile('a1b2c3d4', 'Foo Bar', '0000-0002-1825-0097')

    db.session.add(profile)
    db.session.commit()

    response = test_client.get('/profiles/a1b2c3d4')

    assert response.status_code == 200
    assert response.headers.get(
        'Content-Type') == 'application/vnd.elife.profile+json;version=1'
    assert json.loads(response.data.decode('UTF-8'))['id'] == 'a1b2c3d4'


def test_profile_not_found(test_client: FlaskClient) -> None:
    response = test_client.get('/profiles/foo')

    assert response.status_code == 404
    assert response.headers.get('Content-Type') == 'application/problem+json'
