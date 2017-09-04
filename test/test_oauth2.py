from json import dumps, loads
from urllib.parse import urlencode

import responses


def test_authorizing_requires_a_client_id(test_client):
    response = test_client.get('/oauth2/authorize')

    assert response.status_code == 400
    assert 'Invalid client_id' in response.data.decode('UTF-8')


def test_authorizing_requires_a_valid_client_id(test_client):
    response = test_client.get('/oauth2/authorize', query_string={'client_id': 'foo'})

    assert response.status_code == 400
    assert 'Invalid client_id' in response.data.decode('UTF-8')


def test_authorizing_requires_a_redirect_uri(test_client):
    response = test_client.get('/oauth2/authorize', query_string={'client_id': 'client_id'})

    assert response.status_code == 400
    assert 'Invalid redirect_uri' in response.data.decode('UTF-8')


def test_authorizing_requires_a_valid_redirect_uri(test_client):
    response = test_client.get('/oauth2/authorize',
                               query_string={'client_id': 'client_id',
                                             'redirect_uri': 'http://www.evil.com/'})

    assert response.status_code == 400
    assert 'Invalid redirect_uri' in response.data.decode('UTF-8')


def test_it_redirects_when_authorizing(test_client):
    response = test_client.get('/oauth2/authorize',
                               query_string={
                                   'client_id': 'client_id',
                                   'redirect_uri': 'http://www.example.com/client/redirect',
                               })

    assert response.status_code == 302
    assert response.headers['Location'] == 'http://www.example.com/server/authorize?' + urlencode(
        {'client_id': 'server_client_id', 'response_type': 'code', 'scope': 'scope',
         'redirect_uri': 'http://localhost/oauth2/check',
         'state': dumps({'redirect_uri': 'http://www.example.com/client/redirect',
                         'client_id': 'client_id', 'original': ''})})


def test_it_requires_a_code_when_checking(test_client):
    response = test_client.get('/oauth2/check')

    assert response.status_code == 400
    assert 'Invalid code' in response.data.decode('UTF-8')


def test_it_requires_a_state_when_checking(test_client):
    response = test_client.get('/oauth2/check', query_string={'code': 1234})

    assert response.status_code == 400
    assert 'Invalid state' in response.data.decode('UTF-8')


def test_it_requires_a_json_state_when_checking(test_client):
    response = test_client.get('/oauth2/check', query_string={'code': 1234, 'state': 'foo'})

    assert response.status_code == 400
    assert 'Invalid state' in response.data.decode('UTF-8')


def test_it_requires_client_id_in_state_when_checking(test_client):
    response = test_client.get('/oauth2/check', query_string={'code': 1234, 'state': dumps(
        {'redirect_uri': 'http://www.example.com/client/redirect', 'client_id': 'foo',
         'original': ''})})

    assert response.status_code == 400
    assert 'Invalid state (client_id)' in response.data.decode('UTF-8')


def test_it_requires_redirect_uri_in_state_when_checking(test_client):
    response = test_client.get('/oauth2/check', query_string={'code': 1234, 'state': dumps(
        {'redirect_uri': 'http://www.evil.com', 'client_id': 'client_id', 'original': ''})})

    assert response.status_code == 400
    assert 'Invalid state (redirect_uri)' in response.data.decode('UTF-8')


def test_it_requires_original_in_state_when_checking(test_client):
    response = test_client.get('/oauth2/check', query_string={'code': 1234, 'state': dumps(
        {'redirect_uri': 'http://www.example.com/client/redirect', 'client_id': 'client_id'})})

    assert response.status_code == 400
    assert 'Invalid state (original)' in response.data.decode('UTF-8')


def test_it_redirects_when_checking(test_client):
    response = test_client.get('/oauth2/check', query_string={'code': 1234, 'state': dumps(
        {'redirect_uri': 'http://www.example.com/client/redirect', 'client_id': 'client_id',
         'original': ''})})

    assert response.status_code == 302
    assert response.headers['Location'] == 'http://www.example.com/client/redirect?' + urlencode(
        {'code': 1234, 'state': ''})


def test_it_redirects_when_checking_but_has_an_error(test_client):
    response = test_client.get('/oauth2/check',
                               query_string={
                                   'error': 'access_denied',
                                   'state': dumps({
                                       'redirect_uri': 'http://www.example.com/client/redirect',
                                       'client_id': 'client_id',
                                       'original': ''
                                   })
                               })

    assert response.status_code == 302
    assert response.headers['Location'] == 'http://www.example.com/client/redirect?' + urlencode(
        {'error': 'access_denied', 'state': ''})


def test_it_requires_client_id_when_exchanging(test_client):
    response = test_client.post('/oauth2/token')

    assert response.status_code == 400
    assert response.headers.get('Content-Type') == 'application/problem+json'
    assert loads(response.data.decode('UTF-8')) == {'title': 'Invalid client_id'}


def test_it_requires_client_secret_when_exchanging(test_client):
    response = test_client.post('/oauth2/token', data={'client_id': 'client_id'})

    assert response.status_code == 400
    assert response.headers.get('Content-Type') == 'application/problem+json'
    assert loads(response.data.decode('UTF-8')) == {'title': 'Invalid client_secret'}


def test_it_requires_redirect_uri_when_exchanging(test_client):
    response = test_client.post('/oauth2/token',
                                data={'client_id': 'client_id', 'client_secret': 'client_secret'})

    assert response.status_code == 400
    assert response.headers.get('Content-Type') == 'application/problem+json'
    assert loads(response.data.decode('UTF-8')) == {'title': 'Invalid redirect_uri'}


def test_it_requires_grant_type_when_exchanging(test_client):
    response = test_client.post('/oauth2/token',
                                data={'client_id': 'client_id', 'client_secret': 'client_secret',
                                      'redirect_uri': 'http://www.example.com/client/redirect'})

    assert response.status_code == 400
    assert response.headers.get('Content-Type') == 'application/problem+json'
    assert loads(response.data.decode('UTF-8')) == {'title': 'Invalid grant_type'}


def test_it_requires_code_when_exchanging(test_client):
    response = test_client.post('/oauth2/token',
                                data={'client_id': 'client_id', 'client_secret': 'client_secret',
                                      'redirect_uri': 'http://www.example.com/client/redirect',
                                      'grant_type': 'authorization_code'})

    assert response.status_code == 400
    assert response.headers.get('Content-Type') == 'application/problem+json'
    assert loads(response.data.decode('UTF-8')) == {'title': 'Invalid code'}


@responses.activate
def test_it_exchanges(test_client):
    responses.add(responses.POST, 'http://www.example.com/server/token', status=200,
                  json={'access_token': '1/fFAGRNJru1FTz70BzhT3Zg', 'expires_in': 3920,
                        'foo': 'bar', 'token_type': 'Bearer'})

    response = test_client.post('/oauth2/token',
                                data={'client_id': 'client_id', 'client_secret': 'client_secret',
                                      'redirect_uri': 'http://www.example.com/client/redirect',
                                      'grant_type': 'authorization_code', 'code': '1234'})

    assert response.status_code == 200
    assert response.headers.get('Content-Type') == 'application/json'
    assert loads(response.data.decode('UTF-8')) == {'access_token': '1/fFAGRNJru1FTz70BzhT3Zg',
                                                    'expires_in': 3920, 'token_type': 'Bearer'}


@responses.activate
def test_it_requires_access_token_when_exchanging(test_client):
    responses.add(responses.POST, 'http://www.example.com/server/token', status=200,
                  json={'expires_in': 3920, 'token_type': 'Bearer'})

    response = test_client.post('/oauth2/token',
                                data={'client_id': 'client_id', 'client_secret': 'client_secret',
                                      'redirect_uri': 'http://www.example.com/client/redirect',
                                      'grant_type': 'authorization_code', 'code': '1234'})

    assert response.status_code == 500
    assert response.headers.get('Content-Type') == 'application/problem+json'


@responses.activate
def test_it_requires_expires_in_when_exchanging(test_client):
    responses.add(responses.POST, 'http://www.example.com/server/token', status=200,
                  json={'access_token': '1/fFAGRNJru1FTz70BzhT3Zg', 'token_type': 'Bearer'})

    response = test_client.post('/oauth2/token',
                                data={'client_id': 'client_id', 'client_secret': 'client_secret',
                                      'redirect_uri': 'http://www.example.com/client/redirect',
                                      'grant_type': 'authorization_code', 'code': '1234'})

    assert response.status_code == 500
    assert response.headers.get('Content-Type') == 'application/problem+json'


@responses.activate
def test_it_requires_a_bearer_token_type_when_exchanging(test_client):
    responses.add(responses.POST, 'http://www.example.com/server/token', status=200,
                  json={'access_token': '1/fFAGRNJru1FTz70BzhT3Zg', 'expires_in': 3920,
                        'token_type': 'foo'})

    response = test_client.post('/oauth2/token',
                                data={'client_id': 'client_id', 'client_secret': 'client_secret',
                                      'redirect_uri': 'http://www.example.com/client/redirect',
                                      'grant_type': 'authorization_code', 'code': '1234'})

    assert response.status_code == 500
    assert response.headers.get('Content-Type') == 'application/problem+json'


@responses.activate
def test_it_requires_authorization_when_fetching_user_details(test_client):
    response = test_client.get('/oauth2/user')

    assert response.status_code == 401
    assert response.headers.get('Content-Type') == 'application/problem+json'
    assert loads(response.data.decode('UTF-8')) == {'title': 'Requires authorization'}


@responses.activate
def test_it_fetches_user_details(test_client):
    responses.add(responses.GET, 'http://www.example.com/server/user', status=200,
                  headers={'Authorization': 'Bearer bazqux'}, json={'name': 'Foo Bar'})

    response = test_client.get('/oauth2/user', headers={'Authorization': 'Bearer bazqux'})

    assert response.status_code == 200
    assert response.headers.get('Content-Type') == 'application/json'
    assert loads(response.data.decode('UTF-8')) == {'name': 'Foo Bar'}
