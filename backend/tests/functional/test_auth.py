def test_register_success_201(client):
    r = client.post("/api/auth/register", json={"username": "newuser", "password": "pass1234"})
    assert r.status_code == 201


def test_register_returns_user_public_fields(client):
    r = client.post("/api/auth/register", json={"username": "alice", "password": "pass1234"})
    data = r.json()
    assert "id" in data
    assert data["username"] == "alice"
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_id_is_integer(client):
    r = client.post("/api/auth/register", json={"username": "alice", "password": "pass1234"})
    assert isinstance(r.json()["id"], int)


def test_register_duplicate_username_returns_400(client):
    client.post("/api/auth/register", json={"username": "alice", "password": "pass1234"})
    r = client.post("/api/auth/register", json={"username": "alice", "password": "pass9999"})
    assert r.status_code == 400


def test_register_empty_username_422(client):
    r = client.post("/api/auth/register", json={"username": "", "password": "pass1234"})
    assert r.status_code == 422


def test_register_username_too_long_422(client):
    r = client.post("/api/auth/register", json={"username": "a" * 65, "password": "pass1234"})
    assert r.status_code == 422


def test_register_password_too_short_422(client):
    r = client.post("/api/auth/register", json={"username": "bob", "password": "abc"})
    assert r.status_code == 422


def test_register_multiple_users_get_unique_ids(client):
    r1 = client.post("/api/auth/register", json={"username": "user1", "password": "pass1234"})
    r2 = client.post("/api/auth/register", json={"username": "user2", "password": "pass1234"})
    assert r1.json()["id"] != r2.json()["id"]


def test_login_success_returns_token(client):
    client.post("/api/auth/register", json={"username": "alice", "password": "pass1234"})
    r = client.post("/api/auth/token", data={"username": "alice", "password": "pass1234"})
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_token_is_nonempty_string(client):
    client.post("/api/auth/register", json={"username": "alice", "password": "pass1234"})
    r = client.post("/api/auth/token", data={"username": "alice", "password": "pass1234"})
    token = r.json()["access_token"]
    assert isinstance(token, str) and len(token) > 0


def test_login_wrong_password_401(client):
    client.post("/api/auth/register", json={"username": "alice", "password": "pass1234"})
    r = client.post("/api/auth/token", data={"username": "alice", "password": "wrongpass"})
    assert r.status_code == 401


def test_login_nonexistent_user_401(client):
    r = client.post("/api/auth/token", data={"username": "nobody", "password": "pass1234"})
    assert r.status_code == 401


def test_login_returns_www_authenticate_on_failure(client):
    r = client.post("/api/auth/token", data={"username": "x", "password": "wrongpass"})
    assert r.status_code == 401
