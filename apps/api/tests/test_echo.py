def test_http_echo(client):
    r = client.get("/api/echo?message=Ping")
    assert r.status_code == 200
    assert r.json()["echo"] == "Ping"
