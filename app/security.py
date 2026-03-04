import jwt
import secrets
from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from .config import settings

# Initialize password hasher - Argon2
password_hash = PasswordHash((Argon2Hasher(),)).recommended()


# Hashing password using plain text password
def hash_password(password: str) -> str:
    """Hash a plain text password using Argon2."""
    return password_hash.hash(password)

# Verify plain text passowrd with received hashed_password
def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a plain text password against a stored hashed password."""
    return password_hash.verify(password, hashed_password)

# Access access_token creation, default role: user
def create_access_token(subject: str | int, role: str = "user") -> str:
    """
    Create a short-lived, Asymmetric JWT access token using PRIVATE_KEY
    subject or sub would most likely be the user id or email, and role can be used for authorization purposes.
    """
    expires = datetime.now(timezone.utc) + timedelta(minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # JWT payload - these details will be encoded to a JWT string using Public Key
    to_encode = {
        "sub": str(subject),
        "role": role,
        "exp": expires,
        "iat": datetime.now(timezone.utc)   #Issued at time.
    }

    # Load the private key
    with open(settings.PRIVATE_KEY_PATH, "rb") as key_file:
        private_key = key_file.read()

    # Sign using RS256 algorithm
    encoded_jwt = jwt.encode(to_encode, private_key, algorithm = settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token() -> str:
    """
    Creates a long-lived opaque token (secure random string).
    We will hash this string before storing it in the database.
    """
    return secrets.token_urlsafe(64)