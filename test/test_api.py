import json
from typing import Callable

from flask.testing import FlaskClient
from iso3166 import countries
from werkzeug.datastructures import Headers

from profiles.models import Address, Affiliation, Date, Name, Profile, db
from profiles.utilities import contains_none_values, validate_json


def test_empty_list_of_profiles(test_client: FlaskClient) -> None:
    response = test_client.get('/profiles')

    assert response.status_code == 200
    assert response.headers.get('Cache-Control') == 'max-age=300, public, stale-if-error=86400,' \
                                                    'stale-while-revalidate=300'
    assert response.headers.get(
        'Content-Type') == 'application/vnd.elife.profile-list+json;version=1'
    assert response.headers.get('Vary') == 'Accept'

    data = json.loads(response.data.decode('UTF-8'))

    assert data['total'] == 0
    assert not data['items']
    assert validate_json(data, schema_name='profile-list.v1') is True


def test_list_of_profiles_revalidation(test_client: FlaskClient) -> None:
    response = test_client.get('/profiles')

    assert response.status_code == 200
    assert 'ETag' in response.headers

    response = test_client.get('/profiles', headers={'If-None-Match': response.headers.get('ETag')})

    assert response.status_code == 304

    response = test_client.get('/profiles', headers={'If-None-Match': 'foo'})

    assert response.status_code == 200


def test_list_of_profiles(test_client: FlaskClient, commit: Callable[[], None]) -> None:
    for number in range(1, 31):
        number = str(number).zfill(2)
        db.session.add(Profile(str(number), Name('Profile %s' % number)))
    commit()

    response = test_client.get('/profiles')

    assert response.status_code == 200
    assert response.headers.get(
        'Content-Type') == 'application/vnd.elife.profile-list+json;version=1'

    data = json.loads(response.data.decode('UTF-8'))

    assert validate_json(data, schema_name='profile-list.v1') is True
    assert data['total'] == 30
    assert len(data['items']) == 20
    for number in range(20, 0):
        assert data['items'][number - 1]['id'] == str(number).zfill(2)


def test_list_of_profiles_only_contains_snippets(test_client: FlaskClient,
                                                 commit: Callable[[], None]) -> None:
    profile = Profile('a1b2c3d4', Name('Foo Bar'), '0000-0002-1825-0097')
    profile.add_email_address('foo@example.com')

    db.session.add(profile)
    commit()

    response = test_client.get('/profiles')

    data = json.loads(response.data.decode('UTF-8'))

    assert validate_json(data, schema_name='profile-list.v1') is True
    assert 'emailAddresses' not in data['items'][0]


def test_list_of_profiles_in_ascending_order(test_client: FlaskClient,
                                             commit: Callable[[], None]) -> None:
    for number in range(1, 31):
        number = str(number).zfill(2)
        db.session.add(Profile(str(number), Name('Profile %s' % number)))
    commit()

    response = test_client.get('/profiles?order=asc')

    assert response.status_code == 200
    assert response.headers.get(
        'Content-Type') == 'application/vnd.elife.profile-list+json;version=1'

    data = json.loads(response.data.decode('UTF-8'))

    assert validate_json(data, schema_name='profile-list.v1') is True
    assert data['total'] == 30
    assert len(data['items']) == 20
    for number in range(1, 21):
        assert data['items'][number - 1]['id'] == str(number).zfill(2)


def test_list_of_profiles_in_pages(test_client: FlaskClient, commit: Callable[[], None]) -> None:
    for number in range(1, 11):
        number = str(number).zfill(2)
        db.session.add(Profile(str(number), Name('Profile %s' % number)))
    commit()

    response = test_client.get('/profiles?page=1&per-page=5')

    assert response.status_code == 200
    assert response.headers.get(
        'Content-Type') == 'application/vnd.elife.profile-list+json;version=1'

    data = json.loads(response.data.decode('UTF-8'))

    assert validate_json(data, schema_name='profile-list.v1') is True
    assert data['total'] == 10
    assert len(data['items']) == 5
    for number in range(5, 0):
        assert data['items'][number - 1]['id'] == str(number).zfill(2)

    response = test_client.get('/profiles?page=2&per-page=5')

    assert response.status_code == 200
    assert response.headers.get(
        'Content-Type') == 'application/vnd.elife.profile-list+json;version=1'

    data = json.loads(response.data.decode('UTF-8'))

    assert validate_json(data, schema_name='profile-list.v1') is True
    assert data['total'] == 10
    assert len(data['items']) == 5
    for number in range(5, 0):
        assert data['items'][number - 1]['id'] == str(number + 5).zfill(2)


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


def test_400s_on_unknown_order(test_client: FlaskClient) -> None:
    response = test_client.get('/profiles?order=foo')

    assert response.status_code == 400
    assert response.headers.get('Content-Type') == 'application/problem+json'


def test_get_profile(test_client: FlaskClient, commit: Callable[[], None]) -> None:
    profile = Profile('a1b2c3d4', Name('Foo Bar'), '0000-0002-1825-0097')

    db.session.add(profile)
    commit()

    response = test_client.get('/profiles/a1b2c3d4')

    assert response.status_code == 200
    assert response.headers.get('Cache-Control') == 'max-age=300, public, stale-if-error=86400,' \
                                                    'stale-while-revalidate=300'
    assert response.headers.get('Content-Type') == 'application/vnd.elife.profile+json;version=1'
    assert response.headers.get('Vary') == 'Accept'

    data = json.loads(response.data.decode('UTF-8'))

    assert validate_json(data, schema_name='profile.v1') is True
    assert data['id'] == 'a1b2c3d4'


def test_get_profile_revalidation(test_client: FlaskClient, commit: Callable[[], None]) -> None:
    profile = Profile('a1b2c3d4', Name('Foo Bar'), '0000-0002-1825-0097')

    db.session.add(profile)
    commit()

    response = test_client.get('/profiles/a1b2c3d4')

    assert response.status_code == 200
    assert 'ETag' in response.headers

    response = test_client.get('/profiles/a1b2c3d4',
                               headers={'If-None-Match': response.headers.get('ETag')})

    assert response.status_code == 304

    response = test_client.get('/profiles/a1b2c3d4', headers={'If-None-Match': 'foo'})

    assert response.status_code == 200


def test_profile_not_found(test_client: FlaskClient) -> None:
    response = test_client.get('/profiles/foo')

    assert response.status_code == 404
    assert response.headers.get('Content-Type') == 'application/problem+json'


def test_get_profile_response_contains_email_addresses(test_client: FlaskClient,
                                                       commit: Callable[[], None]) -> None:
    profile = Profile('a1b2c3d4', Name('Foo Bar'), '0000-0002-1825-0097')
    profile.add_email_address('1@example.com')
    profile.add_email_address('2@example.com')

    db.session.add(profile)
    commit()

    response = test_client.get('/profiles/a1b2c3d4')
    data = json.loads(response.data.decode('UTF-8'))

    assert response.status_code == 200
    assert response.headers.get('Content-Type') == 'application/vnd.elife.profile+json;version=1'
    assert validate_json(data, schema_name='profile.v1') is True
    assert len(data['emailAddresses']) == 2


def test_does_not_contain_restricted_email_addresses(test_client: FlaskClient,
                                                     commit: Callable[[], None]) -> None:
    profile = Profile('a1b2c3d4', Name('Foo Bar'), '0000-0002-1825-0097')
    profile.add_email_address('1@example.com')
    profile.add_email_address('2@example.com', restricted=True)

    db.session.add(profile)
    commit()

    response = test_client.get('/profiles/a1b2c3d4')
    data = json.loads(response.data.decode('UTF-8'))

    assert response.status_code == 200
    assert response.headers.get('Content-Type') == 'application/vnd.elife.profile+json;version=1'
    assert validate_json(data, schema_name='profile.v1') is True
    assert [e['value'] for e in data['emailAddresses']] == ['1@example.com']


def test_get_profile_response_contains_affiliations(test_client: FlaskClient, yesterday,
                                                    commit: Callable[[], None]) -> None:
    address = Address(country=countries.get('gb'), city='City', region='Region')
    affiliation = Affiliation('1', address=address, organisation='Org', department='Dep',
                              starts=yesterday)

    profile = Profile('a1b2c3d4', Name('Foo Bar'), '0000-0002-1825-0097')

    db.session.add(profile)
    profile.add_affiliation(affiliation)

    commit()

    response = test_client.get('/profiles/a1b2c3d4')
    data = json.loads(response.data.decode('UTF-8'))

    assert response.status_code == 200
    assert response.headers.get('Content-Type') == 'application/vnd.elife.profile+json;version=1'
    assert validate_json(data, schema_name='profile.v1') is True
    assert len(data['affiliations']) == 1


def test_it_does_not_return_restricted_affiliations(test_client: FlaskClient, yesterday,
                                                    commit: Callable[[], None]) -> None:
    address = Address(country=countries.get('gb'), city='City', region='Region')
    affiliation = Affiliation('1', address=address, organisation='Org', department='Dep',
                              starts=yesterday)

    affiliation2 = Affiliation('2', address=address, organisation='Org2', department='Dep2',
                               starts=yesterday, restricted=True)

    profile = Profile('a1b2c3d4', Name('Foo Bar'), '0000-0002-1825-0097')

    db.session.add(profile)

    profile.add_affiliation(affiliation)
    profile.add_affiliation(affiliation2)

    commit()

    response = test_client.get('/profiles/a1b2c3d4')
    data = json.loads(response.data.decode('UTF-8'))

    assert response.status_code == 200
    assert response.headers.get('Content-Type') == 'application/vnd.elife.profile+json;version=1'
    assert validate_json(data, schema_name='profile.v1') is True
    assert [e['value']['name'] for e in data['affiliations']] == [['Dep', 'Org']]


def test_it_does_return_restricted_data_when_authenticated(
        test_client: FlaskClient, yesterday: Date, commit: Callable[[], None]) -> None:

    address = Address(country=countries.get('gb'), city='City', region='Region')
    affiliation = Affiliation('1', address=address, organisation='Org', department='Dep',
                              starts=yesterday, restricted=True)

    profile = Profile('a1b2c3d4', Name('Foo Bar'), '0000-0002-1825-0097')
    profile.add_email_address('1@example.com', restricted=True)
    profile.add_affiliation(affiliation)

    db.session.add(profile)
    commit()

    headers = Headers()
    headers.set('X-Consumer-Groups', 'View-restricted-profiles, Something else')
    response = test_client.get('/profiles/a1b2c3d4', headers=headers)
    data = json.loads(response.data.decode('UTF-8'))

    assert response.status_code == 200
    assert response.headers.get('Content-Type') == 'application/vnd.elife.profile+json;version=1'
    assert validate_json(data, schema_name='profile.v1') is True
    assert len(data['affiliations']) == 1
    assert len(data['emailAddresses']) == 1
    assert [e['value'] for e in data['emailAddresses']] == ['1@example.com']
    assert [e['value']['name'] for e in data['affiliations']] == [['Dep', 'Org']]


def test_it_does_not_return_restricted_data_when_authenticated(
        test_client: FlaskClient, yesterday: Date, commit: Callable[[], None]) -> None:

    address = Address(country=countries.get('gb'), city='City', region='Region')
    affiliation = Affiliation('1', address=address, organisation='Org', department='Dep',
                              starts=yesterday, restricted=True)

    profile = Profile('a1b2c3d4', Name('Foo Bar'), '0000-0002-1825-0097')
    profile.add_email_address('1@example.com', restricted=True)
    profile.add_affiliation(affiliation)

    db.session.add(profile)
    commit()

    response = test_client.get('/profiles/a1b2c3d4')
    data = json.loads(response.data.decode('UTF-8'))

    assert response.status_code == 200
    assert response.headers.get('Content-Type') == 'application/vnd.elife.profile+json;version=1'
    assert validate_json(data, schema_name='profile.v1') is True
    assert not data['affiliations']
    assert not data['emailAddresses']


def test_it_does_not_return_null_values_in_response(test_client: FlaskClient,
                                                    yesterday: Date,
                                                    commit: Callable[[], None]) -> None:

    address = Address(country=countries.get('gb'),
                      city='City',
                      region=None)  # produces null value when serialized
    affiliation = Affiliation('2',
                              address=address,
                              organisation='Org',
                              department=None,  # produces null value when serialized
                              starts=yesterday,
                              restricted=False)

    profile = Profile('a1b2c3d4', Name('Foo Bar'), '0000-0002-1825-0097')
    profile.add_email_address('1@example.com', restricted=False)
    profile.add_affiliation(affiliation)

    db.session.add(profile)
    commit()

    headers = Headers()
    headers.set('X-Consumer-Groups', 'View-restricted-profiles, Something else')
    response = test_client.get('/profiles/a1b2c3d4', headers=headers)
    data = json.loads(response.data.decode('UTF-8'))

    assert response.status_code == 200, response.status_code
    assert response.headers.get('Content-Type') == 'application/vnd.elife.profile+json;version=1'
    assert validate_json(data, schema_name='profile.v1') is True
    assert contains_none_values(data) is False
