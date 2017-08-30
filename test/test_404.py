import json


def test_it_handles_404s(test_client):
    response = test_client.get('/')

    assert response.status_code == 404
    assert response.headers.get('Content-Type') == 'application/problem+json'
    assert json.loads(response.data.decode('UTF-8')) == {'title': 'Not Found'}
