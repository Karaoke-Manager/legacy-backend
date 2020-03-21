from werkzeug import Client, Response


def test_songs(client: Client):
    response: Response = client.get('/songs/1')
    assert response.status_code == 200
