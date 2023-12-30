"""의존성을 정의합니다."""
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import AsyncSessionLocal

__all__ = ("get_db",)


async def get_db() -> AsyncSession:
    """데이터베이스 세션을 반환합니다."""
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    finally:
        await session.close()
