"""소설 관련 서비스를 제공합니다."""
# pylint: disable=redefined-builtin
import logging

import requests
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.domain.base.service import to_dto
from src.domain.novels.crud import CRUDChapter, CRUDNovel
from src.domain.novels.models import Chapter, ChapterMemo, Novel, NovelMemo
from src.domain.novels.schemas import (
    ChapterDTO,
    ChapterMemoCreate,
    ChapterMemoUpdate,
    ChaptersDTO,
    ChaptersRequest,
    NovelCreate,
    NovelDTO,
    NovelMemoCreate,
    NovelMemoDTO,
    NovelsDTO,
    NovelsRequest,
)
from src.libs.responses import NovelError

logger = logging.getLogger(__name__)


@to_dto.register(Novel)
def _(obj: Novel) -> NovelDTO:
    """Novel 객체를 NovelDTO 객체로 변환합니다."""
    return NovelDTO.model_validate(obj)


@to_dto.register(NovelMemo)
def _(obj: NovelMemo) -> NovelMemoDTO:
    """NovelMemo 객체를 NovelMemoDTO 객체로 변환합니다."""
    return NovelMemoDTO.model_validate(obj)


@to_dto.register(Chapter)
def _(obj: Chapter) -> ChapterDTO:
    """Chapter 객체를 ChapterDTO 객체로 변환합니다."""
    return ChapterDTO.model_validate(obj)


class NovelService:
    """소설 관련 서비스"""

    def __init__(self, db: AsyncSession):
        self.crud_novel = CRUDNovel(db)

    async def create(self, command: NovelCreate) -> NovelDTO:
        """소설을 생성합니다."""
        if await self.crud_novel.get_by_platform_id(command.platform, command.id):
            raise NovelError.NOVEL_ALREADY_EXISTS.http_exception

        response = requests.post(
            settings.NOVEL_FETCH_URL, json=command.model_dump(mode="json", exclude_none=True), timeout=30
        )

        if response.status_code == 400:
            exception = NovelError.NOVEL_CREATE_FAILED.http_exception
            exception.detail = response.json()["detail"]
            raise exception

        if response.status_code == 404:
            raise NovelError.NOVEL_NOT_FOUND.http_exception

        if response.status_code != 200:
            logger.error("알 수 없는 이유로 소설 생성에 실패했습니다. %s %s", response.status_code, response.text)
            raise NovelError.UNEXPECTED_ERROR.http_exception

        return NovelDTO(**response.json())

    @classmethod
    @property
    def create_errors(cls) -> tuple:
        """에러 메시지"""
        return (
            NovelError.NOVEL_ALREADY_EXISTS,
            NovelError.NOVEL_CREATE_FAILED,
            NovelError.NOVEL_NOT_FOUND,
            NovelError.UNEXPECTED_ERROR,
        )

    async def get(self, id: int) -> NovelDTO:
        """소설을 조회합니다."""
        item = await self.crud_novel.get(id)
        if not item:
            raise NovelError.NOVEL_NOT_FOUND.http_exception
        return to_dto(item)

    @classmethod
    @property
    def get_errors(cls) -> tuple:
        """에러 메시지"""
        return (NovelError.NOVEL_NOT_FOUND,)

    async def get_multi(self, command: NovelsRequest) -> NovelsDTO:
        """소설 목록을 조회합니다."""
        items = await self.crud_novel.get_multi(**command.model_dump())
        return NovelsDTO(items=items)

    async def get_memo(self, novel_id: int, user_id: int) -> NovelMemoDTO:
        """소설 메모를 조회합니다."""
        if not (item := await self.crud_novel.get_memo(novel_id, user_id)):
            return NovelMemoDTO(novel_id=novel_id, user_id=user_id)
        return to_dto(item)

    async def create_memo(self, command: NovelMemoCreate) -> NovelMemoDTO:
        """소설 메모를 생성합니다."""
        # Dependency
        await self.get(command.novel_id)
        if await self.crud_novel.get_memo(command.novel_id, command.user_id, content_existed=False):
            raise NovelError.NOVEL_MEMO_ALREADY_EXISTS.http_exception

        item = await self.crud_novel.create_memo(**command.model_dump())
        return to_dto(item)

    async def update_memo(self, command: NovelMemoCreate) -> NovelMemoDTO:
        """소설 메모를 수정합니다."""
        # Dependency
        await self.get(command.novel_id)
        item = await self.crud_novel.create_memo(**command.model_dump())
        return to_dto(item)

    async def delete_memo(self, novel_id: int, user_id: int) -> NovelMemoDTO:
        """소설 메모를 삭제합니다."""
        # Dependency
        await self.get(novel_id)
        if memo := await self.crud_novel.delete_memo(novel_id, user_id):
            return to_dto(memo)
        return NovelMemoDTO(novel_id=novel_id, user_id=user_id)

    @classmethod
    @property
    def create_memo_errors(cls) -> tuple:
        """에러 메시지"""
        return cls.get_errors + (NovelError.NOVEL_MEMO_ALREADY_EXISTS,)

    @classmethod
    @property
    def update_memo_errors(cls) -> tuple:
        """에러 메시지"""
        return cls.get_errors

    async def mark_as_favorite(self, novel_id: int, user_id: int) -> NovelMemoDTO:
        """소설을 즐겨찾기에 추가합니다."""
        # Dependency
        await self.get(novel_id)
        item = await self.crud_novel.mark_as_favorite(novel_id, user_id)
        return to_dto(item)

    async def unmark_as_favorite(self, novel_id: int, user_id: int) -> NovelMemoDTO:
        """소설을 즐겨찾기에서 제거합니다."""
        # Dependency
        await self.get(novel_id)
        if item := await self.crud_novel.unmark_as_favorite(novel_id, user_id):
            return to_dto(item)
        return NovelMemoDTO(novel_id=novel_id, user_id=user_id)


class ChapterService:
    """소설 챕터 관련 서비스"""

    def __init__(self, db: AsyncSession):
        self.crud_chapter = CRUDChapter(db)

    async def get(self, id: int) -> Chapter:
        """소설 챕터를 조회합니다."""
        item = await self.crud_chapter.get(id)
        if not item:
            raise NovelError.CHAPTER_NOT_FOUND.http_exception
        return item

    @classmethod
    @property
    def get_errors(cls) -> tuple:
        """에러 메시지"""
        return (NovelError.CHAPTER_NOT_FOUND,)

    async def get_multi(self, novel_id: int, command: ChaptersRequest, user_id: int | None = None) -> ChaptersDTO:
        """소설 챕터 목록을 조회합니다."""
        items = await self.crud_chapter.get_multi(novel_id, **command.model_dump(), user_id=user_id)
        return ChaptersDTO(items=items)

    async def get_memo(self, chapter_id: int, user_id: int) -> ChapterMemo:
        """소설 챕터 메모를 조회합니다."""
        if not (item := await self.crud_chapter.get_memo(chapter_id, user_id)):
            raise NovelError.CHAPTER_MEMO_NOT_FOUND.http_exception
        return item

    @classmethod
    @property
    def get_memo_errors(cls) -> tuple:
        """에러 메시지"""
        return (NovelError.CHAPTER_MEMO_NOT_FOUND,)

    async def create_memo(self, command: ChapterMemoCreate) -> ChapterMemo:
        """소설 챕터 메모를 생성합니다."""
        # Dependency
        await self.get(command.chapter_id)
        if await self.crud_chapter.get_memo(command.chapter_id, command.user_id):
            raise NovelError.CHAPTER_MEMO_ALREADY_EXISTS.http_exception

        item = await self.crud_chapter.create_memo(**command.model_dump())
        return item

    @classmethod
    @property
    def create_memo_errors(cls) -> tuple:
        """에러 메시지"""
        return cls.get_errors + (NovelError.CHAPTER_MEMO_ALREADY_EXISTS,)

    async def update_memo(self, command: ChapterMemoUpdate) -> ChapterMemo:
        """소설 챕터 메모를 수정합니다."""
        # Dependency
        await self.get_memo(command.chapter_id, command.user_id)
        item = await self.crud_chapter.create_memo(**command.model_dump())
        return item

    async def delete_memo(self, chapter_id: int, user_id: int) -> None:
        """소설 챕터 메모를 삭제합니다."""
        # Dependency
        await self.get_memo(chapter_id, user_id)
        await self.crud_chapter.delete_memo(chapter_id, user_id)
