def test_otp_request(client):
    r = client.post("/api/auth/otp/request", json={"email":"test@example.com"})
    assert r.status_code == 200
    assert "expires_in" in r.json()
