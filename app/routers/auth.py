import hashlib

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.concurrency import run_in_threadpool
from datetime import datetime, timedelta, timezone

from app.database import db

from app.database import db
from .. import schemas, security, dependencies
from ..database.db import get_session
from ..database.models import User, RefreshToken
from ..config import settings

router = APIRouter(prefix="/auth")

# function to hash refresh_token using hashlib.sha256
def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


"""
1. /api/v1/auth/register/
    - receives email and password
    - check if user exist - using db session
    - if user doesn't exist, it creates one
        - fist hash password using run_in_threadpool which opens a new theread and run Hashing as it is slow process
        - creates a new user
        - add to the database
        - commit and refresh
        - return new user

"""
@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: schemas.UserCreate, db: AsyncSession = Depends(get_session)):
    query = select(User).where(User.email == user_in.email)
    result = await db.exec(query)
    if result.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists with this email.",
        )

    hashed_password = await run_in_threadpool(security.hash_password, user_in.password)
    new_user = User(email=user_in.email, hashed_password=hashed_password)
    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user.",
        )
    return new_user


"""
2. /api/v1/auth/login/
    - receives email as username and password
    - check if user exist - using db session
    - if user doesn't exist, it return 401
    - creates access_token and raw_refresh_token
    - create db_refresh_token object, hash refresh_token and add to RefreshToken table
    - return access_token, refresh_token and token_type

"""
@router.post("/login", response_model=schemas.TokenResponse)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_session)):
    query = select(User).where(User.email == form_data.username)
    res = await db.exec(query)
    user = res.first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    access_token = security.create_access_token(
        subject=str(user.id), role=user.role)
    raw_refresh_token = security.create_refresh_token()

    db_refresh_token = RefreshToken(
        user_id=user.id,
        hashed_token=hash_token(raw_refresh_token),
        expires_at=datetime.now(
            timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(db_refresh_token)
    await db.commit()

    return {"access_token": access_token, "refresh_token": raw_refresh_token, "token_type": "bearer"}

"""
3. /api/v1/auth/refresh/
    - receives refresh_token
    - hash the refresh_token and search it in RefreshToken table
    - if token is not in db or it's revoked or it's expired then return Invalid or Expiry 401
    - if token is not expire then get the user_id from RefreshToken table row and find the user in database
    - check if user is still active. If not, return the inactive_user
    - revoke the refresh_token
    - create a new access_token and refresh_token and return them to the user

"""
@router.post("/refresh", response_model=schemas.TokenResponse)
async def refresh_token(refresh_request: schemas.RefreshRequest, db: AsyncSession = Depends(get_session)):
    token_hash = hash_token(refresh_request.refresh_token)
    query = select(RefreshToken).where(RefreshToken.hashed_token == token_hash)
    res = await db.exec(query)
    db_token = res.first()

    current_time = datetime.now(timezone.utc).replace(tzinfo=None)
    if not db_token or db_token.is_revoked or db_token.expires_at < current_time:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid or expired refresh token.")

    query = select(User).where(User.id == db_token.user_id)
    res = await db.exec(query)
    user = res.first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive.")

    db_token.is_revoked = True

    new_access_token = security.create_access_token(
        subject=str(user.id), role=user.role)
    new_raw_refresh_token = security.create_refresh_token()
    new_db_refresh_token = RefreshToken(
        user_id=user.id,
        hashed_token=hash_token(new_raw_refresh_token),
        expires_at=datetime.now(
            timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(new_db_refresh_token)
    await db.commit()
    return {"access_token": new_access_token, "refresh_token": new_raw_refresh_token, "token_type": "bearer"}
