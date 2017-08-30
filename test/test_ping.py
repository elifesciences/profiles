def test_it_pongs(test_client):
    response = test_client.get('/ping')

    assert 200 == response.status_code
    assert 'pong' == response.data.decode('UTF-8')
    assert 'text/plain; charset=UTF-8' == response.headers.get('Content-Type')
