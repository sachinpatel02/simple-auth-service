from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from functools import lru_cache
import jwt
import uuid


from .database.db import get_session
from .database.models import User
from .config import settings
from app.core.redis import redis_client

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@lru_cache(maxsize=1)
def get_public_key():
    with open(settings.PUBLIC_KEY_PATH, "rb") as key_file:
        return key_file.read()


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_session)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    is_blocked = await redis_client.get(f"blocklist:{token}")
    if is_blocked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This token has been revoked. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        public_key = get_public_key()
        payload = jwt.decode(token, public_key, algorithms=[
                             settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise credentials_exception
    user_id_in_db = uuid.UUID(user_id)
    query = select(User).where(User.id == user_id_in_db)
    res = await db.exec(query)
    user = res.first()
    if user is None:
        raise credentials_exception
    return user
