"""database session과 관련된 기능을 정의합니다."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import settings

__all__ = ["AsyncSessionLocal"]


engine = create_async_engine(str(settings.DB_PATH), pool_pre_ping=True, echo=settings.DEBUG)

AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False, autocommit=False
)
