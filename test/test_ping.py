from flask.testing import FlaskClient


def test_it_pongs(test_client: FlaskClient) -> None:
    response = test_client.get('/ping')

    assert response.status_code == 200
    assert response.data.decode('UTF-8') == 'pong'
    assert response.headers.get('Content-Type') == 'text/plain; charset=UTF-8'
