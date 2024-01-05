"""의존성을 정의합니다."""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from src.core.security import decode_jwt_token, oauth2_scheme, oauth2_scheme_optional
from src.db import AsyncSessionLocal
from src.domain.auth.schemas import TokenPayload

__all__ = ("get_db",)


async def get_db() -> AsyncSession:
    """데이터베이스 세션을 반환합니다."""
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    finally:
        await session.close()


async def get_token_payload(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> TokenPayload:
    """토큰의 payload를 반환합니다."""
    return TokenPayload(**decode_jwt_token(token))


async def get_token_payload_optional(
    token: Annotated[str | None, Depends(oauth2_scheme_optional)],
) -> TokenPayload | None:
    """토큰의 payload를 반환합니다."""
    if token:
        return TokenPayload(**decode_jwt_token(token))
    return None
