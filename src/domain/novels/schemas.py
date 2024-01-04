"""소설 DTO 정의"""
# pylint: disable=redefined-builtin
from datetime import datetime
from enum import Enum

from pydantic import ConfigDict, Field, HttpUrl, model_validator
from typing_extensions import Annotated

from src.domain.base.schemas import DTO, Base
from src.libs.responses import NovelError
from src.libs.utils import parse_last_path

__all__ = (
    "Platform",
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

    @model_validator(mode="after")
    @classmethod
    def parse_novel_id(cls, data: "NovelCreate"):
        """소설 아이디를 가져옵니다."""
        if data.id:
            return data

        if not data.url:
            raise NovelError.NEED_NOVEL_REF.http_exception

        if data.platform == Platform.RIDI:
            data.id = parse_last_path(str(data.url), is_digit=True)
        return data

    @classmethod
    @property
    def errors(cls) -> tuple:
        """에러 메시지"""
        return (NovelError.NEED_NOVEL_REF,)
