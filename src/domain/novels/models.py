"""데이터베이스 모델."""
from datetime import datetime
from enum import Enum

from sqlalchemy import BOOLEAN, INTEGER, TEXT, TIMESTAMP, VARCHAR, ForeignKey, Index, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.base.models import Base

__all__ = (
    "NovelCategory",
    "Novel",
    "NovelMemo",
    "Chapter",
    "ChapterMemo",
)


class NovelCategory(str, Enum):
    """소설 카테고리."""

    FANTASY = "판타지"
    MODERN_FANTASY = "현대판타지"
    WUXIA = "무협"
    ROMANCE = "로맨스"
    ROMANCE_FANTASY = "로맨스판타지"

    def __str__(self) -> str:
        """문자열로 변환합니다."""

        return self.value


class Novel(Base):
    """소설."""

    __tablename__ = "novels"

    id: Mapped[int] = mapped_column(primary_key=True, type_=INTEGER, autoincrement=True, comment="ID")
    title: Mapped[str] = mapped_column(VARCHAR(255), nullable=False, comment="제목")
    description: Mapped[str] = mapped_column(TEXT, comment="설명")
    author: Mapped[str] = mapped_column(VARCHAR(255), comment="작가")
    published_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), comment="공개일")
    last_updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), comment="최종 업데이트일")
    category: Mapped[NovelCategory] = mapped_column(VARCHAR(20), nullable=False, comment="카테고리")
    ridi_id: Mapped[str] = mapped_column(VARCHAR(20), unique=True, comment="리디북스 아이디")
    kakao_id: Mapped[str] = mapped_column(VARCHAR(20), unique=True, comment="카카오 페이지 아이디")
    series_id: Mapped[str] = mapped_column(VARCHAR(20), unique=True, comment="시리즈 아이디")
    munpia_id: Mapped[str] = mapped_column(VARCHAR(20), unique=True, comment="문피아 아이디")
    image_url: Mapped[str] = mapped_column(VARCHAR(255), comment="이미지 URL")

    __table_args__ = (
        Index("novels_title_author_idx", title, author),
        {"comment": "소설"},
    )


class NovelMemo(Base):
    """소설 메모."""

    __tablename__ = "novel_memos"

    novel_id: Mapped[int] = mapped_column(INTEGER, ForeignKey("novels.id"), nullable=False, comment="소설 아이디 (외래 키)")
    user_id: Mapped[int] = mapped_column(INTEGER, ForeignKey("users.id"), nullable=False, comment="사용자 아이디 (외래 키)")
    content: Mapped[str] = mapped_column(TEXT, comment="내용")
    average_star: Mapped[float] = mapped_column(INTEGER, comment="평균 별점")
    is_favorite: Mapped[bool] = mapped_column(BOOLEAN, comment="즐겨찾기 여부", default=False, nullable=False)
    modified_at: Mapped[datetime] = mapped_column("content_updated_at", TIMESTAMP(timezone=True), comment="내용 수정일")

    __table_args__ = (
        PrimaryKeyConstraint(novel_id, user_id),
        Index("novel_memos_user_id_idx", user_id),
        {"comment": "소설 메모"},
    )


class Chapter(Base):
    """소설 챕터."""

    __tablename__ = "chapters"

    id: Mapped[int] = mapped_column(primary_key=True, type_=INTEGER, autoincrement=True, comment="ID")
    novel_id: Mapped[int] = mapped_column(INTEGER, ForeignKey("novels.id"), nullable=False, comment="소설 아이디 (외래 키)")
    chapter_no: Mapped[int] = mapped_column(INTEGER, nullable=False, comment="챕터 번호")
    title: Mapped[str] = mapped_column(VARCHAR(255), nullable=False, comment="제목")
    published_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), comment="공개일")
    ridi_id: Mapped[str] = mapped_column(VARCHAR(20), unique=True, comment="리디북스 아이디")
    kakao_id: Mapped[str] = mapped_column(VARCHAR(20), unique=True, comment="카카오 페이지 아이디")
    series_id: Mapped[str] = mapped_column(VARCHAR(20), unique=True, comment="시리즈 아이디")
    munpia_id: Mapped[str] = mapped_column(VARCHAR(20), unique=True, comment="문피아 아이디")

    __table_args__ = (
        Index("chapters_novel_id_chapter_no_idx", novel_id, chapter_no.desc()),
        Index("chapters_chapter_no_idx", chapter_no.desc()),
        {"comment": "소설 챕터"},
    )


class ChapterMemo(Base):
    """챕터 메모."""

    __tablename__ = "chapter_memos"

    chapter_id: Mapped[int] = mapped_column(INTEGER, ForeignKey("chapters.id"), nullable=False, comment="챕터 아이디 (외래 키)")
    user_id: Mapped[int] = mapped_column(INTEGER, ForeignKey("users.id"), nullable=False, comment="사용자 아이디 (외래 키)")
    content: Mapped[str] = mapped_column(TEXT, comment="내용")
    star: Mapped[int] = mapped_column(INTEGER, comment="별점")

    __table_args__ = (
        PrimaryKeyConstraint(chapter_id, user_id),
        Index("chapter_memos_user_id_idx", user_id),
        {"comment": "챕터 메모"},
    )
