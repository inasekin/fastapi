from datetime import UTC, datetime, timedelta

import bcrypt
from jose import JWTError, jwt

from app.config import settings
from app.schemas import TokenPayload


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_access_token(subject: str) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> TokenPayload | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return TokenPayload(sub=payload.get("sub"))
    except JWTError:
        return None
