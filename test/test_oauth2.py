from json import dumps, loads
from unittest.mock import MagicMock, patch
from urllib.parse import urlencode

from flask.testing import FlaskClient
from freezegun import freeze_time
import responses

from profiles.models import OrcidToken, Profile, db
from profiles.utilities import expires_at


def test_authorizing_requires_a_client_id(test_client: FlaskClient) -> None:
    response = test_client.get('/oauth2/authorize')

    assert response.status_code == 400
    assert 'Invalid client_id' in response.data.decode('UTF-8')


def test_authorizing_requires_a_valid_client_id(test_client: FlaskClient) -> None:
    response = test_client.get('/oauth2/authorize', query_string={'client_id': 'foo'})

    assert response.status_code == 400
    assert 'Invalid client_id' in response.data.decode('UTF-8')


def test_authorizing_requires_a_valid_redirect_uri(test_client: FlaskClient) -> None:
    response = test_client.get('/oauth2/authorize',
                               query_string={'client_id': 'client_id',
                                             'redirect_uri': 'http://www.evil.com/'})

    assert response.status_code == 400
    assert 'Invalid redirect_uri' in response.data.decode('UTF-8')


def test_authorizing_requires_a_response_type(test_client: FlaskClient) -> None:
    response = test_client.get('/oauth2/authorize', query_string={'client_id': 'client_id'})

    assert response.status_code == 302
    assert response.headers['Location'] == 'http://www.example.com/client/redirect?' + urlencode(
        {'error': 'invalid_request', 'error_description': 'Missing response_type'}, True)


def test_authorizing_requires_a_valid_response_type(test_client: FlaskClient) -> None:
    response = test_client.get('/oauth2/authorize',
                               query_string={'client_id': 'client_id', 'response_type': 'foo'})

    assert response.status_code == 302
    assert response.headers['Location'] == 'http://www.example.com/client/redirect?' + urlencode(
        {'error': 'unsupported_response_type'}, True)


def test_it_rejects_scope_when_authorizing(test_client: FlaskClient) -> None:
    response = test_client.get('/oauth2/authorize',
                               query_string={'client_id': 'client_id', 'response_type': 'code',
                                             'scope': 'foo'})

    assert response.status_code == 302
    assert response.headers['Location'] == 'http://www.example.com/client/redirect?' + urlencode(
        {'error': 'invalid_scope'}, True)


def test_it_redirects_when_authorizing(test_client: FlaskClient) -> None:
    response = test_client.get('/oauth2/authorize',
                               query_string={'client_id': 'client_id', 'response_type': 'code'})

    assert response.status_code == 302
    assert response.headers['Location'] == 'http://www.example.com/server/authorize?' + urlencode(
        {'client_id': 'server_client_id', 'response_type': 'code', 'scope': '/read-limited',
         'redirect_uri': 'http://localhost/oauth2/check',
         'state': dumps({'redirect_uri': 'http://www.example.com/client/redirect',
                         'client_id': 'client_id'}, sort_keys=True)}, True)


def test_it_redirects_with_the_original_state_when_authorizing(test_client: FlaskClient) -> None:
    response = test_client.get('/oauth2/authorize',
                               query_string={'client_id': 'client_id', 'response_type': 'code',
                                             'state': 'foo'})

    assert response.status_code == 302
    assert response.headers['Location'] == 'http://www.example.com/server/authorize?' + urlencode(
        {'client_id': 'server_client_id', 'response_type': 'code', 'scope': '/read-limited',
         'redirect_uri': 'http://localhost/oauth2/check',
         'state': dumps({'redirect_uri': 'http://www.example.com/client/redirect',
                         'client_id': 'client_id', 'original': 'foo'}, sort_keys=True)}, True)


def test_it_requires_a_code_when_checking(test_client: FlaskClient) -> None:
    response = test_client.get('/oauth2/check')

    assert response.status_code == 400
    assert 'Invalid code' in response.data.decode('UTF-8')


def test_it_requires_a_state_when_checking(test_client: FlaskClient) -> None:
    response = test_client.get('/oauth2/check', query_string={'code': 1234})

    assert response.status_code == 400
    assert 'Invalid state' in response.data.decode('UTF-8')


def test_it_requires_a_json_state_when_checking(test_client: FlaskClient) -> None:
    response = test_client.get('/oauth2/check', query_string={'code': 1234, 'state': 'foo'})

    assert response.status_code == 400
    assert 'Invalid state' in response.data.decode('UTF-8')


def test_it_requires_client_id_in_state_when_checking(test_client: FlaskClient) -> None:
    response = test_client.get('/oauth2/check', query_string={'code': 1234, 'state': dumps(
        {'redirect_uri': 'http://www.example.com/client/redirect', 'client_id': 'foo'},
        sort_keys=True)})

    assert response.status_code == 400
    assert 'Invalid state (client_id)' in response.data.decode('UTF-8')


def test_it_requires_redirect_uri_in_state_when_checking(test_client: FlaskClient) -> None:
    response = test_client.get('/oauth2/check', query_string={'code': 1234, 'state': dumps(
        {'redirect_uri': 'http://www.evil.com', 'client_id': 'client_id'}, sort_keys=True)})

    assert response.status_code == 400
    assert 'Invalid state (redirect_uri)' in response.data.decode('UTF-8')


def test_it_redirects_when_checking(test_client: FlaskClient) -> None:
    response = test_client.get('/oauth2/check', query_string={'code': 1234, 'state': dumps(
        {'redirect_uri': 'http://www.example.com/client/redirect', 'client_id': 'client_id'},
        sort_keys=True)})

    assert response.status_code == 302
    assert response.headers['Location'] == 'http://www.example.com/client/redirect?' + urlencode(
        {'code': 1234}, True)


def test_it_redirects_with_the_original_state_when_checking(test_client: FlaskClient) -> None:
    response = test_client.get('/oauth2/check', query_string={'code': 1234, 'state': dumps(
        {'redirect_uri': 'http://www.example.com/client/redirect', 'client_id': 'client_id',
         'original': 'foo'})})

    assert response.status_code == 302
    assert response.headers['Location'] == 'http://www.example.com/client/redirect?' + urlencode(
        {'code': 1234, 'state': 'foo'}, True)


def test_it_redirects_when_checking_but_has_an_error(test_client: FlaskClient) -> None:
    response = test_client.get('/oauth2/check',
                               query_string={
                                   'error': 'access_denied',
                                   'state': dumps({
                                       'redirect_uri': 'http://www.example.com/client/redirect',
                                       'client_id': 'client_id',
                                   }, sort_keys=True)
                               })

    assert response.status_code == 302
    assert response.headers['Location'] == 'http://www.example.com/client/redirect?' + urlencode(
        {'error': 'access_denied'}, True)


def test_it_requires_client_id_when_exchanging(test_client: FlaskClient) -> None:
    response = test_client.post('/oauth2/token')

    assert response.status_code == 401
    assert response.headers.get('Content-Type') == 'application/json'
    assert loads(response.data.decode('UTF-8')) == {'error': 'invalid_client'}


def test_it_requires_client_secret_when_exchanging(test_client: FlaskClient) -> None:
    response = test_client.post('/oauth2/token', data={'client_id': 'client_id'})

    assert response.status_code == 401
    assert response.headers.get('Content-Type') == 'application/json'
    assert loads(response.data.decode('UTF-8')) == {'error': 'invalid_client'}


def test_it_requires_redirect_uri_when_exchanging(test_client: FlaskClient) -> None:
    response = test_client.post('/oauth2/token',
                                data={'client_id': 'client_id', 'client_secret': 'client_secret'})

    assert response.status_code == 400
    assert response.headers.get('Content-Type') == 'application/json'
    assert loads(response.data.decode('UTF-8')) == {'error': 'invalid_request',
                                                    'error_description': 'Invalid redirect_uri'}


def test_it_requires_grant_type_when_exchanging(test_client: FlaskClient) -> None:
    response = test_client.post('/oauth2/token',
                                data={'client_id': 'client_id', 'client_secret': 'client_secret',
                                      'redirect_uri': 'http://www.example.com/client/redirect'})

    assert response.status_code == 400
    assert response.headers.get('Content-Type') == 'application/json'
    assert loads(response.data.decode('UTF-8')) == {'error': 'unsupported_grant_type'}


def test_it_requires_code_when_exchanging(test_client: FlaskClient) -> None:
    response = test_client.post('/oauth2/token',
                                data={'client_id': 'client_id', 'client_secret': 'client_secret',
                                      'redirect_uri': 'http://www.example.com/client/redirect',
                                      'grant_type': 'authorization_code'})

    assert response.status_code == 400
    assert response.headers.get('Content-Type') == 'application/json'
    assert loads(response.data.decode('UTF-8')) == {'error': 'invalid_grant'}


@patch('profiles.repositories.generate_random_string')
@responses.activate
def test_it_exchanges(generate_random_string: MagicMock, test_client: FlaskClient) -> None:
    generate_random_string.return_value = '1a2b3c4e'

    responses.add(responses.POST, 'http://www.example.com/server/token', status=200,
                  json={'access_token': '1/fFAGRNJru1FTz70BzhT3Zg', 'expires_in': 3920,
                        'foo': 'bar', 'token_type': 'Bearer', 'orcid': '0000-0002-1825-0097',
                        'name': 'Josiah Carberry'})

    response = test_client.post('/oauth2/token',
                                data={'client_id': 'client_id', 'client_secret': 'client_secret',
                                      'redirect_uri': 'http://www.example.com/client/redirect',
                                      'grant_type': 'authorization_code', 'code': '1234'})

    assert response.status_code == 200
    assert response.headers.get('Content-Type') == 'application/json'
    assert loads(response.data.decode('UTF-8')) == {'access_token': '1/fFAGRNJru1FTz70BzhT3Zg',
                                                    'expires_in': 3920, 'token_type': 'Bearer',
                                                    'orcid': '0000-0002-1825-0097',
                                                    'name': 'Josiah Carberry', 'id': '1a2b3c4e'}


@responses.activate
def test_it_creates_a_profile_when_exchanging(test_client: FlaskClient) -> None:
    responses.add(responses.POST, 'http://www.example.com/server/token', status=200,
                  json={'access_token': '1/fFAGRNJru1FTz70BzhT3Zg', 'expires_in': 3920,
                        'foo': 'bar', 'token_type': 'Bearer', 'orcid': '0000-0002-1825-0097',
                        'name': 'Joe Bloggs'})
    responses.add(responses.GET, 'http://www.example.com/api/v2.0/0000-0002-1825-0097/record',
                  status=200,
                  json={'person': {'name': {'family-name': {'value': 'Carberry'},
                                            'given-names': {'value': 'Josiah'}}}})

    test_client.post('/oauth2/token',
                     data={'client_id': 'client_id', 'client_secret': 'client_secret',
                           'redirect_uri': 'http://www.example.com/client/redirect',
                           'grant_type': 'authorization_code', 'code': '1234'})

    assert Profile.query.count() == 1

    profile = Profile.query.filter_by(orcid='0000-0002-1825-0097').one()

    assert profile.orcid == '0000-0002-1825-0097'
    assert profile.name == 'Josiah Carberry'


@responses.activate
def test_it_updates_a_profile_when_exchanging(test_client: FlaskClient) -> None:
    responses.add(responses.POST, 'http://www.example.com/server/token', status=200,
                  json={'access_token': '1/fFAGRNJru1FTz70BzhT3Zg', 'expires_in': 3920,
                        'foo': 'bar', 'token_type': 'Bearer', 'orcid': '0000-0002-1825-0097',
                        'name': 'Joe Bloggs'})
    responses.add(responses.GET, 'http://www.example.com/api/v2.0/0000-0002-1825-0097/record',
                  status=200,
                  json={'person': {'name': {'family-name': {'value': 'Carberry'},
                                            'given-names': {'value': 'Josiah'}}}})

    original_profile = Profile('a1b2c3d4', 'Joe Bloggs', '0000-0002-1825-0097')

    db.session.add(original_profile)
    db.session.commit()

    test_client.post('/oauth2/token',
                     data={'client_id': 'client_id', 'client_secret': 'client_secret',
                           'redirect_uri': 'http://www.example.com/client/redirect',
                           'grant_type': 'authorization_code', 'code': '1234'})

    assert Profile.query.count() == 1
    assert original_profile.name == 'Josiah Carberry'


@freeze_time('2017-09-15 14:36:43')
@responses.activate
def test_it_records_the_access_token_when_exchanging(test_client: FlaskClient) -> None:
    responses.add(responses.POST, 'http://www.example.com/server/token', status=200,
                  json={'access_token': '1/fFAGRNJru1FTz70BzhT3Zg', 'expires_in': 3920,
                        'foo': 'bar', 'token_type': 'Bearer', 'orcid': '0000-0002-1825-0097',
                        'name': 'Josiah Carberry'})

    response = test_client.post('/oauth2/token',
                                data={'client_id': 'client_id', 'client_secret': 'client_secret',
                                      'redirect_uri': 'http://www.example.com/client/redirect',
                                      'grant_type': 'authorization_code', 'code': '1234'})

    assert response.status_code == 200

    assert OrcidToken.query.count() == 1

    orcid_token = OrcidToken.query.filter_by(orcid='0000-0002-1825-0097').one()

    assert orcid_token.access_token == '1/fFAGRNJru1FTz70BzhT3Zg'
    assert orcid_token.expires_at == expires_at(3920)


@freeze_time('2017-09-15 14:36:43')
@responses.activate
def test_it_updates_the_access_token_when_exchanging(test_client: FlaskClient) -> None:
    responses.add(responses.POST, 'http://www.example.com/server/token', status=200,
                  json={'access_token': '1/fFAGRNJru1FTz70BzhT3Zg', 'expires_in': 3920,
                        'foo': 'bar', 'token_type': 'Bearer', 'orcid': '0000-0002-1825-0097',
                        'name': 'Josiah Carberry'})

    original_orcid_token = OrcidToken('0000-0002-1825-0097', 'old-access-token', expires_at(1234))

    db.session.add(original_orcid_token)
    db.session.commit()

    test_client.post('/oauth2/token',
                     data={'client_id': 'client_id', 'client_secret': 'client_secret',
                           'redirect_uri': 'http://www.example.com/client/redirect',
                           'grant_type': 'authorization_code', 'code': '1234'})

    assert OrcidToken.query.count() == 1
    assert original_orcid_token.access_token == '1/fFAGRNJru1FTz70BzhT3Zg'
    assert original_orcid_token.expires_at == expires_at(3920)


@responses.activate
def test_it_requires_access_token_when_exchanging(test_client: FlaskClient) -> None:
    responses.add(responses.POST, 'http://www.example.com/server/token', status=200,
                  json={'expires_in': 3920, 'token_type': 'Bearer'})

    response = test_client.post('/oauth2/token',
                                data={'client_id': 'client_id', 'client_secret': 'client_secret',
                                      'redirect_uri': 'http://www.example.com/client/redirect',
                                      'grant_type': 'authorization_code', 'code': '1234'})

    assert response.status_code == 500
    assert response.headers.get('Content-Type') == 'application/problem+json'


@responses.activate
def test_it_requires_expires_in_when_exchanging(test_client: FlaskClient) -> None:
    responses.add(responses.POST, 'http://www.example.com/server/token', status=200,
                  json={'access_token': '1/fFAGRNJru1FTz70BzhT3Zg', 'token_type': 'Bearer'})

    response = test_client.post('/oauth2/token',
                                data={'client_id': 'client_id', 'client_secret': 'client_secret',
                                      'redirect_uri': 'http://www.example.com/client/redirect',
                                      'grant_type': 'authorization_code', 'code': '1234'})

    assert response.status_code == 500
    assert response.headers.get('Content-Type') == 'application/problem+json'


@responses.activate
def test_it_requires_a_bearer_token_type_when_exchanging(test_client: FlaskClient) -> None:
    responses.add(responses.POST, 'http://www.example.com/server/token', status=200,
                  json={'access_token': '1/fFAGRNJru1FTz70BzhT3Zg', 'expires_in': 3920,
                        'token_type': 'foo'})

    response = test_client.post('/oauth2/token',
                                data={'client_id': 'client_id', 'client_secret': 'client_secret',
                                      'redirect_uri': 'http://www.example.com/client/redirect',
                                      'grant_type': 'authorization_code', 'code': '1234'})

    assert response.status_code == 500
    assert response.headers.get('Content-Type') == 'application/problem+json'
