import json
from flask.testing import FlaskClient


def test_it_handles_404s(test_client: FlaskClient):
    response = test_client.get('/')

    assert response.status_code == 404
    assert response.headers.get('Content-Type') == 'application/problem+json'
    assert json.loads(response.data.decode('UTF-8')) == {
        'title': 'The requested URL was not found on the server.  If you entered the URL manually '
                 'please check your spelling and try again.'}
