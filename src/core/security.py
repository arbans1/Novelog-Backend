"""앱의 보안 관련 유틸리티 함수를 정의합니다."""
from datetime import datetime, timedelta

import bcrypt
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from src.core.config import settings
from src.libs.responses import UserError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    비밀번호를 검증합니다.

    Args:
        plain_password (str): 평문 비밀번호
        hashed_password (str): 해시된 비밀번호
    """
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def get_password_hash(password: str) -> str:
    """
    비밀번호를 해시합니다.

    Args:
        password (str): 평문 비밀번호
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode()


def create_jwt_token(data: dict, expires_minutes: int = 15) -> str:
    """JWT 토큰을 생성합니다.

    Args:
        data (dict): 토큰에 담을 데이터
        expires_minutes (int): 토큰 만료 시간. Defaults to 15.

    Returns:
        str: JWT 토큰
    """
    to_encode = data.copy()
    expires_delta = timedelta(minutes=expires_minutes)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY.get_secret_value(), algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_jwt_token(token: str) -> dict:
    """JWT 토큰을 디코딩합니다.

    Args:
        token (str): JWT 토큰

    Returns:
        dict: 디코딩된 JWT 토큰
    """
    credentials_exception = UserError.CREDENTIALS_EXCEPTION.http_exception
    credentials_exception.headers = {"WWW-Authenticate": "Bearer"}
    try:
        return jwt.decode(token, settings.SECRET_KEY.get_secret_value(), algorithms=[settings.JWT_ALGORITHM])
    except JWTError as exc:
        raise credentials_exception from exc
