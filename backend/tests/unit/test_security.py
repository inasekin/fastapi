from datetime import UTC, datetime, timedelta

from jose import jwt

from app.config import settings
from app.schemas import TokenPayload
from app.security import create_access_token, decode_token, hash_password, verify_password


def test_hash_password_returns_bcrypt_hash():
    hashed = hash_password("mysecretpassword")
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")


def test_hash_password_produces_different_salts():
    h1 = hash_password("password")
    h2 = hash_password("password")
    assert h1 != h2


def test_verify_password_correct():
    hashed = hash_password("mypassword")
    assert verify_password("mypassword", hashed) is True


def test_verify_password_wrong():
    hashed = hash_password("mypassword")
    assert verify_password("wrongpassword", hashed) is False


def test_verify_password_empty_wrong():
    hashed = hash_password("mypassword")
    assert verify_password("", hashed) is False


def test_create_access_token_returns_string():
    token = create_access_token("42")
    assert isinstance(token, str)
    assert len(token) > 0


def test_create_access_token_is_valid_jwt():
    token = create_access_token("99")
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    assert payload["sub"] == "99"


def test_decode_token_valid_sub():
    token = create_access_token("99")
    payload = decode_token(token)
    assert payload is not None
    assert payload.sub == "99"


def test_decode_token_preserves_sub():
    token = create_access_token("user_123")
    payload = decode_token(token)
    assert payload.sub == "user_123"


def test_decode_token_returns_token_payload_type():
    token = create_access_token("5")
    payload = decode_token(token)
    assert isinstance(payload, TokenPayload)


def test_decode_token_invalid_returns_none():
    payload = decode_token("not.a.valid.jwt.token")
    assert payload is None


def test_decode_token_garbage_returns_none():
    payload = decode_token("garbage123")
    assert payload is None


def test_decode_token_expired_returns_none():
    expire = datetime.now(UTC) - timedelta(minutes=5)
    to_encode = {"sub": "42", "exp": expire}
    token = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    payload = decode_token(token)
    assert payload is None


def test_decode_token_wrong_secret_returns_none():
    expire = datetime.now(UTC) + timedelta(minutes=60)
    to_encode = {"sub": "42", "exp": expire}
    token = jwt.encode(to_encode, "wrong-secret", algorithm=settings.algorithm)
    payload = decode_token(token)
    assert payload is None
