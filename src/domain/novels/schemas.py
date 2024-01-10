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
    "NovelOrder",
    "NovelsRequest",
    "NovelsDTO",
    "NovelFilter",
    "NovelCategoryFilter",
    "NovelMemoDTO",
    "NovelMemoContent",
    "NovelMemoCreate",
    "ChapterOrder",
    "ChaptersRequest",
    "ChapterDTO",
    "ChaptersDTO",
    "ChapterMemoContent",
    "ChapterMemoContentNull",
    "ChapterMemoCreate",
    "ChapterMemoUpdate",
    "ChapterMemoDTO",
)


class StrEnum(str, Enum):
    """문자열 Enum"""

    def __str__(self) -> str:
        """문자열로 변환합니다."""

        return self.value


class Platform(StrEnum):
    """소설 플랫폼"""

    RIDI = "ridi"
    KAKAO = "kakao"
    SERIES = "series"
    MUNPIA = "munpia"


def id_to_url(id: str, platform: Platform) -> HttpUrl:
    """소설 아이디를 URL로 변환합니다."""
    if platform == Platform.RIDI:
        return HttpUrl(f"https://ridibooks.com/books/{id}")
    raise ValueError(f"지원하지 않는 플랫폼입니다. platform={platform}")


class NovelDTO(DTO):
    """소설 DTO"""

    model_config: ConfigDict = ConfigDict(from_attributes=True)

    id: Annotated[int, Field(description="소설 ID")]
    title: Annotated[str, Field(description="제목")]
    author: Annotated[str, Field(description="작가")]
    description: Annotated[str, Field(description="설명")] = ""
    published_at: Annotated[datetime, Field(description="공개일")]
    last_updated_at: Annotated[datetime, Field(description="최종 업데이트일")]
    category: Annotated[str, Field(description="카테고리")]
    image_url: Annotated[HttpUrl, Field(description="이미지 URL")] = ""
    ridi_id: Annotated[str | None, Field(description="리디북스 아이디", exclude=True)] = None
    kakao_id: Annotated[str | None, Field(description="카카오 페이지 아이디", exclude=True)] = None
    series_id: Annotated[str | None, Field(description="시리즈 아이디", exclude=True)] = None
    munpia_id: Annotated[str | None, Field(description="문피아 아이디", exclude=True)] = None
    ridi_url: Annotated[HttpUrl | None, Field(description="리디북스 URL")] = None
    kakao_url: Annotated[HttpUrl | None, Field(description="카카오 페이지 URL")] = None
    series_url: Annotated[HttpUrl | None, Field(description="시리즈 URL")] = None
    munpia_url: Annotated[HttpUrl | None, Field(description="문피아 URL")] = None
    average_star: Annotated[float | None, Field(description="평균 별점")] = None
    is_favorite: Annotated[bool, Field(description="즐겨찾기 여부")] = False
    content: Annotated[str | None, Field(description="내용")] = None
    modified_at: Annotated[datetime | None, Field(description="내용 수정일")] = None

    @model_validator(mode="after")
    @classmethod
    def id_to_url(cls, data: "NovelDTO"):
        """소설 ID를 URL로 변환"""
        data.ridi_url = id_to_url(data.ridi_id, Platform.RIDI)
        return data


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


class NovelOrder(StrEnum):
    """소설 정렬"""

    TITLE = "title"
    AUTHOR = "author"
    PUBLISHED_AT = "published_at"
    LAST_UPDATED_AT = "last_updated_at"


class NovelFilter(StrEnum):
    """소설 필터"""

    ALL = "all"
    TITLE = "title"
    AUTHOR = "author"
    DESCRIPTION = "description"


class NovelCategoryFilter(StrEnum):
    """소설 카테고리 필터"""

    ALL = "all"
    FANTASY = "fantasy"
    MODERN_FANTASY = "modern_fantasy"
    WUXIA = "wuxia"
    ROMANCE = "romance"
    ROMANCE_FANTASY = "romance_fantasy"


class NovelsRequest(Base):
    """소설 목록 요청"""

    skip: Annotated[int, Field(description="건너뛸 개수", ge=0)] = 0
    limit: Annotated[int | None, Field(description="최대 개수", ge=0, le=100)] = 10
    query: Annotated[str | None, Field(description="검색어")] = None
    filter_by: Annotated[NovelFilter, Field(description="필터 기준")] = NovelFilter.ALL
    category: Annotated[NovelCategoryFilter, Field(description="카테고리 필터")] = NovelCategoryFilter.ALL
    order_by: Annotated[NovelOrder, Field(description="정렬 기준")] = NovelOrder.LAST_UPDATED_AT
    desc: Annotated[bool, Field(description="내림차순 여부")] = True


class NovelsDTO(DTO):
    """소설 목록 DTO"""

    items: Annotated[list[NovelDTO], Field(description="소설 목록")]


class NovelMemoDTO(DTO):
    """소설 메모 DTO"""

    content: Annotated[str | None, Field(description="내용")] = None
    average_star: Annotated[float | None, Field(description="평균 별점")] = None
    is_favorite: Annotated[bool, Field(description="즐겨찾기 여부")] = False
    modified_at: Annotated[datetime | None, Field(description="내용 수정일")] = None


class NovelMemoContent(Base):
    """소설 메모 내용"""

    content: Annotated[str | None, Field(description="내용")] = None


class NovelMemoCreate(NovelMemoContent):
    """소설 메모 생성"""

    novel_id: Annotated[int, Field(description="소설 ID")]
    user_id: Annotated[int, Field(description="사용자 ID")]


class ChapterOrder(StrEnum):
    """챕터 정렬"""

    CHAPTER_NO = "chapter_no"


class ChaptersRequest(Base):
    """챕터 목록 요청"""

    skip: Annotated[int, Field(description="건너뛸 개수", ge=0)] = 0
    limit: Annotated[int | None, Field(description="최대 개수", ge=0, le=100)] = 10
    order_by: Annotated[ChapterOrder, Field(description="정렬 기준")] = ChapterOrder.CHAPTER_NO
    desc: Annotated[bool, Field(description="내림차순 여부")] = True


class ChapterDTO(DTO):
    """챕터 DTO"""

    novel_id: Annotated[int, Field(description="소설 ID")]
    chapter_no: Annotated[int, Field(description="챕터 번호")]
    title: Annotated[str, Field(description="제목")]
    published_at: Annotated[datetime, Field(description="공개일")]
    ridi_id: Annotated[str | None, Field(description="리디북스 아이디", exclude=True)] = None
    kakao_id: Annotated[str | None, Field(description="카카오 페이지 아이디", exclude=True)] = None
    series_id: Annotated[str | None, Field(description="시리즈 아이디", exclude=True)] = None
    munpia_id: Annotated[str | None, Field(description="문피아 아이디", exclude=True)] = None
    ridi_url: Annotated[HttpUrl | None, Field(description="리디북스 URL")] = None
    kakao_url: Annotated[HttpUrl | None, Field(description="카카오 페이지 URL")] = None
    series_url: Annotated[HttpUrl | None, Field(description="시리즈 URL")] = None
    munpia_url: Annotated[HttpUrl | None, Field(description="문피아 URL")] = None
    star: Annotated[int | None, Field(description="별점", ge=1, le=10)] = None
    modified_at: Annotated[datetime | None, Field(description="내용 수정일")] = None

    @model_validator(mode="after")
    @classmethod
    def id_to_url(cls, data: "ChapterDTO"):
        """소설 ID를 URL로 변환"""
        data.ridi_url = id_to_url(data.ridi_id, Platform.RIDI)
        return data


class ChaptersDTO(DTO):
    """챕터 목록 DTO"""

    items: Annotated[list[ChapterDTO], Field(description="챕터 목록")]


class ChapterMemoBase(Base):
    """챕터 메모"""

    novel_id: Annotated[int, Field(description="소설 ID")]
    chapter_no: Annotated[int, Field(description="챕터 번호")]
    user_id: Annotated[int, Field(description="사용자 ID")]


class ChapterMemoContentNull(Base):
    """챕터 메모 내용"""

    content: Annotated[str | None, Field(description="내용")] = None
    star: Annotated[int | None, Field(description="별점", ge=1, le=10)] = None


class ChapterMemoContent(Base):
    """챕터 메모 내용"""

    content: Annotated[str, Field(description="내용")]
    star: Annotated[int, Field(description="별점", ge=1, le=10)]


class ChapterMemoCreate(ChapterMemoBase, ChapterMemoContent):
    """챕터 메모 생성"""


class ChapterMemoUpdate(ChapterMemoBase, ChapterMemoContentNull):
    """챕터 메모 수정"""


class ChapterMemoDTO(DTO, ChapterMemoBase, ChapterMemoContent):
    """챕터 메모 DTO"""

    novel_id: Annotated[int, Field(description="소설 ID")]
    updated_at: Annotated[datetime, Field(description="내용 수정일")]
