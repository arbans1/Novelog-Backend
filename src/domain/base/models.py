"""데이터베이스의 모델을 위한 기본 클래스"""
# pylint: disable=not-callable
from datetime import datetime, timezone

from sqlalchemy import TIMESTAMP, func
from sqlalchemy.orm import DeclarativeBase  # pylint: disable=E0401
from sqlalchemy.orm import Mapped, mapped_column
from typing_extensions import TypeVar

__all__ = ("Base", "Model")


class Base(DeclarativeBase):  # pylint: disable=R0903
    """데이터베이스 모델을 위한 기본 클래스"""

    __abstract__ = True
    __tablename__: str

    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.utcnow().replace(tzinfo=timezone.utc),
        server_default=func.now(),
        type_=TIMESTAMP(timezone=True),
        comment="생성일",
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.utcnow().replace(tzinfo=timezone.utc),
        server_default=func.now(),
        onupdate=func.now(),
        type_=TIMESTAMP(timezone=True),
        comment="수정일",
    )


Model = TypeVar("Model", bound=Base)
