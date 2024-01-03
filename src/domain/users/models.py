"""유저 모델을 정의한 모듈입니다."""

from datetime import datetime

from sqlalchemy import TIMESTAMP, VARCHAR, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.base.models import Base


class User(Base):
    """사용자"""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column("login_id", nullable=False, unique=True, comment="이메일", type_=VARCHAR(255))
    hashed_password: Mapped[str] = mapped_column(nullable=False, comment="해시된 비밀번호", type_=VARCHAR(72))
    nickname: Mapped[str] = mapped_column(nullable=False, comment="닉네임", type_=VARCHAR(255))
    is_admin: Mapped[bool] = mapped_column(nullable=False, comment="관리자 여부", type_=Boolean)
    is_active: Mapped[bool] = mapped_column(nullable=False, comment="활성화 여부", type_=Boolean)
    deleted_at: Mapped[datetime] = mapped_column(comment="삭제일", type_=TIMESTAMP(timezone=True))
