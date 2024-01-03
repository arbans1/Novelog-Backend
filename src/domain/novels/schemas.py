"""소설 DTO 정의"""
from datetime import datetime
from enum import Enum

from pydantic import ConfigDict, Field, HttpUrl, model_validator
from typing_extensions import Annotated

from src.domain.base.schemas import DTO, Base
from src.libs.responses import NovelError

__all__ = (
    "NovelDTO",
    "NovelCreate",
)


class NovelDTO(DTO):
    """소설 DTO"""

    model_config: ConfigDict = ConfigDict(from_attributes=True)

    id: Annotated[int, Field(description="소설 ID")]
    title: Annotated[str, Field(description="제목")]
    author: Annotated[str, Field(description="작가")]
    description: Annotated[str, Field(description="설명")] = ""
    published_at: Annotated[datetime, Field(description="공개일")]
    category: Annotated[str, Field(description="카테고리")]
    image_url: Annotated[HttpUrl, Field(description="이미지 URL")] = ""
    ridi_url: Annotated[HttpUrl | None, Field(description="리디북스 URL")] = None
    kakao_url: Annotated[HttpUrl | None, Field(description="카카오 페이지 URL")] = None
    series_url: Annotated[HttpUrl | None, Field(description="시리즈 URL")] = None
    munpia_url: Annotated[HttpUrl | None, Field(description="문피아 URL")] = None

    @model_validator(mode="before")
    @classmethod
    def id_to_url(cls, data):
        """소설 ID를 URL로 변환"""
        if data.get("ridi_id"):
            data["ridi_url"] = f"https://ridibooks.com/books/{data['ridi_id']}"
        return data


class Platform(Enum):
    """소설 플랫폼"""

    RIDI = "ridi"
    KAKAO = "kakao"
    SERIES = "series"
    MUNPIA = "munpia"


class NovelCreate(Base):
    """소설 생성"""

    id: Annotated[str | None, Field(description="소설 ID")] = None
    url: Annotated[HttpUrl | None, Field(description="소설 URL")] = None
    platform: Annotated[Platform, Field(description="소설 플랫폼")]

    @classmethod
    @property
    def errors(cls) -> tuple:
        """에러 메시지"""
        return (NovelError.NEED_NOVEL_REF,)
