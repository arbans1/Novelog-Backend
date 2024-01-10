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
    ChapterMemoDTO,
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


@to_dto.register(ChapterMemo)
def _(obj: ChapterMemo) -> ChapterMemoDTO:
    """ChapterMemo 객체를 ChapterMemoDTO 객체로 변환합니다."""
    return ChapterMemoDTO.model_validate(obj)


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

    async def get_with_memo(self, id: int, user_id: int) -> NovelDTO:
        """소설을 조회합니다."""
        item = await self.crud_novel.get(id)
        if not item:
            raise NovelError.NOVEL_NOT_FOUND.http_exception
        new_item: NovelDTO = to_dto(item)
        if memo := await self.crud_novel.get_memo(id, user_id):
            new_item.average_star = memo.average_star
            new_item.is_favorite = memo.is_favorite
            new_item.content = memo.content
            new_item.modified_at = memo.modified_at
        return new_item

    @classmethod
    @property
    def get_errors(cls) -> tuple:
        """에러 메시지"""
        return (NovelError.NOVEL_NOT_FOUND,)

    async def get_multi(self, command: NovelsRequest) -> NovelsDTO:
        """소설 목록을 조회합니다."""
        items = await self.crud_novel.get_multi(**command.model_dump())
        return NovelsDTO(items=items)

    async def get_multi_with_memo(self, command: NovelsRequest, user_id: int) -> NovelsDTO:
        """소설 목록을 조회합니다."""
        items = await self.crud_novel.get_multi(**command.model_dump())
        novel_ids = [item.id for item in items]
        memos = await self.crud_novel.get_memo_multi(user_id, novel_ids)
        memo_dict = {memo.novel_id: memo for memo in memos}
        new_items = []
        for item in items:
            new_item: NovelDTO = to_dto(item)
            if memo := memo_dict.get(item.id):
                new_item.average_star = memo.average_star
                new_item.is_favorite = memo.is_favorite
                new_item.content = memo.content
                new_item.modified_at = memo.modified_at
            new_items.append(new_item)
        return NovelsDTO(items=new_items)

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

    async def update_average_star(self, novel_id: int, user_id: int) -> NovelDTO:
        """소설의 평균 별점을 업데이트합니다."""
        # Dependency
        await self.get(novel_id)
        item = await self.crud_novel.update_average_star(novel_id, user_id)
        return to_dto(item)

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

    async def get(self, novel_id: int, chapter_no: int) -> ChapterDTO:
        """소설 챕터를 조회합니다."""
        item = await self.crud_chapter.get(novel_id, chapter_no)
        if not item:
            raise NovelError.CHAPTER_NOT_FOUND.http_exception
        return to_dto(item)

    async def get_with_memo(self, novel_id: int, chapter_no: int, user_id: int) -> ChapterDTO:
        """소설 챕터를 조회합니다."""
        item = await self.crud_chapter.get(novel_id, chapter_no)
        if not item:
            raise NovelError.CHAPTER_NOT_FOUND.http_exception
        new_item: ChapterDTO = to_dto(item)
        if memo := await self.crud_chapter.get_memo(novel_id, chapter_no, user_id):
            new_item.star = memo.star
            new_item.updated_at = memo.updated_at
        return new_item

    @classmethod
    @property
    def get_errors(cls) -> tuple:
        """에러 메시지"""
        return (NovelError.CHAPTER_NOT_FOUND,)

    async def get_multi(self, novel_id: int, command: ChaptersRequest) -> ChaptersDTO:
        """소설 챕터 목록을 조회합니다."""
        items = await self.crud_chapter.get_multi(novel_id, **command.model_dump())
        return ChaptersDTO(items=items)

    async def get_multi_with_memo(self, novel_id: int, command: ChaptersRequest, user_id: int) -> ChaptersDTO:
        """소설 챕터 목록을 조회합니다."""
        items = await self.crud_chapter.get_multi(novel_id, **command.model_dump())
        chapter_nos = [item.chapter_no for item in items]
        memos = await self.crud_chapter.get_memo_multi(novel_id, user_id, chapter_nos)
        memo_dict = {memo.chapter_no: memo for memo in memos}
        new_items = []
        for item in items:
            new_item: ChapterDTO = to_dto(item)
            if memo := memo_dict.get(item.chapter_no):
                new_item.star = memo.star
                new_item.updated_at = memo.updated_at
            new_items.append(new_item)
        return ChaptersDTO(items=new_items)

    async def get_memo(self, novel_id: int, chapter_no: int, user_id: int) -> ChapterMemoDTO:
        """소설 챕터 메모를 조회합니다."""
        if not (item := await self.crud_chapter.get_memo(novel_id, chapter_no, user_id)):
            raise NovelError.CHAPTER_MEMO_NOT_FOUND.http_exception
        return item

    @classmethod
    @property
    def get_memo_errors(cls) -> tuple:
        """에러 메시지"""
        return (NovelError.CHAPTER_MEMO_NOT_FOUND,)

    async def create_memo(self, command: ChapterMemoCreate) -> ChapterMemoDTO:
        """소설 챕터 메모를 생성합니다."""
        # Dependency
        await self.get(command.novel_id, command.chapter_no)
        if await self.crud_chapter.get_memo(command.novel_id, command.chapter_no, command.user_id):
            raise NovelError.CHAPTER_MEMO_ALREADY_EXISTS.http_exception

        item = await self.crud_chapter.create_memo(**command.model_dump())
        return to_dto(item)

    @classmethod
    @property
    def create_memo_errors(cls) -> tuple:
        """에러 메시지"""
        return cls.get_errors + (NovelError.CHAPTER_MEMO_ALREADY_EXISTS,)

    async def update_memo(self, command: ChapterMemoUpdate) -> ChapterMemoDTO:
        """소설 챕터 메모를 수정합니다."""
        # Dependency
        item = await self.crud_chapter.update_memo(**command.model_dump())
        if not item:
            raise NovelError.CHAPTER_MEMO_NOT_FOUND.http_exception
        return to_dto(item)

    async def delete_memo(self, novel_id: int, chapter_no: int, user_id: int) -> ChapterMemoDTO:
        """소설 챕터 메모를 삭제합니다."""
        # Dependency
        item = await self.crud_chapter.delete_memo(novel_id, chapter_no, user_id)
        if not item:
            raise NovelError.CHAPTER_MEMO_NOT_FOUND.http_exception
        return to_dto(item)
