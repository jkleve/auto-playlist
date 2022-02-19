

def test_messages_redirect(client):
    response = client.post("/messages", json={"msg": "Hello, tests"})
    assert response.status_code == 308


def test_messages(client):
    response = client.post("/messages/", json={"msg": "Hello, tests"})
    assert response.status_code == 200
