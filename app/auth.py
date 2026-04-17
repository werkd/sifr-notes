import os

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from passlib.context import CryptContext
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User

# Hashing password


_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)

# Session Cookie - signed token.


_SECRET_KEY = os.environ.get("SECRET_KEY")
if not _SECRET_KEY:
    raise RuntimeError("SECRET_KEY Environment variable is not set.")

SESSION_COOKIE_NAME = "sifr_session"
SESSION_MAX_AGE = int(os.environ.get("SESSION_MAX_AGE_SECONDS", 60*60*24*7))

_serializer = URLSafeTimedSerializer(_SECRET_KEY, salt="sifr-session")


def create_session_token(user_id: int) -> str:
    return _serializer.dumps(user_id)


def decode_session_token(token: str) -> int:
    """
    Returns user_id on sucess
    Raises BadSignature or SignatureExpired on Failure, callers must handle both.
    """
    return _serializer.loads(token, max_age=SESSION_MAX_AGE)


# dependency for auth

class NotAuthenticatedException(Exception):
    """Raised by get_current_user when no valid session exists. """
    pass


async def get_current_user(
        request: Request,
        db: AsyncSession = Depends(get_db),
        ) -> User:
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        raise NotAuthenticatedException()
    
    try:
        user_id = decode_session_token(token)
    except (BadSignature, SignatureExpired):
        raise NotAuthenticatedException()
    
    user = await db.get(User, user_id)
    if user is None:
        raise NotAuthenticatedException()
    
    return User