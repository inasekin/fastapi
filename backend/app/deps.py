from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    payload = decode_token(token)
    if payload is None or payload.sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        user_id = int(payload.sub)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен",
        )
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден"
        )
    return user
