from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from django.contrib.auth.hashers import check_password, make_password  # ✅ Use Django's
from django.conf import settings
from ninja.security import HttpBearer
from .models import User


# ❌ REMOVE PASSLIB (delete these lines)
# from passlib.context import CryptContext
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash using Django's hasher"""
    return check_password(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using Django's hasher"""
    return make_password(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


class AuthBearer(HttpBearer):
    """JWT Bearer authentication for Django Ninja"""
    
    def authenticate(self, request, token):
        payload = decode_token(token)
        
        if payload is None or payload.get("type") != "access":
            return None
        
        user_id = payload.get("sub")
        if user_id is None:
            return None
        
        try:
            user = User.objects.get(id=user_id, is_active=True)
            return user
        except User.DoesNotExist:
            return None


def authenticate_user(email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    try:
        user = User.objects.get(email=email, is_active=True)
        if check_password(password, user.password):  # ✅ Use Django's check_password
            return user
    except User.DoesNotExist:
        pass
    return None
