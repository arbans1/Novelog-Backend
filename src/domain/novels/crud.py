"""소설 CRUD 관련 모듈입니다."""
# pylint: disable=redefined-builtin,too-many-arguments
from datetime import datetime, timezone

from sqlalchemy import func, or_, select
from typing_extensions import Sequence

from src.domain.base.crud import CRUD
from src.domain.novels.models import Chapter, ChapterMemo, Novel, NovelCategory, NovelMemo
from src.domain.novels.schemas import ChapterOrder, NovelCategoryFilter, NovelFilter, NovelOrder, Platform

__all__ = (
    "CRUDNovel",
    "CRUDChapter",
)


class CRUDNovel(CRUD[Novel]):
    """소설 CRUD 클래스"""

    _filter_columns = {
        NovelFilter.TITLE: Novel.title,
        NovelFilter.AUTHOR: Novel.author,
        NovelFilter.DESCRIPTION: Novel.description,
    }

    _category_columns = {
        NovelCategoryFilter.FANTASY: NovelCategory.FANTASY,
        NovelCategoryFilter.MODERN_FANTASY: NovelCategory.MODERN_FANTASY,
        NovelCategoryFilter.WUXIA: NovelCategory.WUXIA,
        NovelCategoryFilter.ROMANCE: NovelCategory.ROMANCE,
        NovelCategoryFilter.ROMANCE_FANTASY: NovelCategory.ROMANCE_FANTASY,
    }

    _order_columns = {
        NovelOrder.AUTHOR: Novel.author,
        NovelOrder.TITLE: Novel.title,
        NovelOrder.PUBLISHED_AT: Novel.published_at,
        NovelOrder.LAST_UPDATED_AT: Novel.last_updated_at,
    }

    async def get(
        self,
        id: int,
    ) -> Novel | None:
        """소설을 조회합니다.

        Args:
            id (int): 소설의 id입니다.

        Returns:
            Novel|None: 소설 객체입니다.
        """
        stmt = select(Novel).where(Novel.id == id)
        return (await self.db.scalars(stmt)).first()

    async def get_by_platform_id(
        self,
        platform: Platform,
        platform_id: str,
    ) -> Novel | None:
        """소설을 조회합니다.

        Args:
            id (int): 소설의 id입니다.

        Returns:
            Novel|None: 소설 객체입니다.
        """
        stmt = select(Novel).where(getattr(Novel, f"{platform}_id") == platform_id)
        return (await self.db.scalars(stmt)).first()

    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int | None = None,
        query: str | None = None,
        filter_by: NovelFilter = NovelFilter.ALL,
        category: NovelCategoryFilter = NovelCategoryFilter.ALL,
        order_by: NovelOrder = NovelOrder.LAST_UPDATED_AT,
        desc: bool = True,
    ) -> Sequence[Novel]:
        """소설 목록을 조회합니다.

        Args:
            skip (int): 건너뛸 개수입니다. Defaults to 0.
            limit (int, optional): 최대 개수입니다. Defaults to None.
            query (str, optional): 검색어입니다. Defaults to None.
            filter_by (NovelFilter): 필터 기준입니다. Defaults to NovelFilter.ALL.
            order_by (NovelOrder): 정렬 기준입니다. Defaults to NovelOrder.LAST_UPDATED_AT.
            desc (bool): 내림차순 여부입니다. Defaults to True.

        Returns:
            Sequence[Novel]: 소설 목록입니다.
        """
        stmt = select(Novel)
        if query:
            escape_query = query.replace("%", r"\%").replace("_", r"\_")
            like_expr = f"%{escape_query}%"
            filter_column = self._filter_columns.get(filter_by)
            stmt = stmt.where(
                filter_column.ilike(like_expr)
                if filter_column
                else or_(
                    Novel.title.ilike(like_expr),
                    Novel.author.ilike(like_expr),
                    Novel.description.ilike(like_expr),
                )
            )
        if catetory_column := self._category_columns.get(category):
            stmt = stmt.where(Novel.category == catetory_column)

        order_column = self._order_columns.get(order_by, Novel.last_updated_at)
        stmt = stmt.order_by(order_column.desc() if desc else order_column).offset(skip)

        if limit:
            stmt = stmt.limit(limit)

        return (await self.db.scalars(stmt)).all()

    async def get_memo(
        self,
        novel_id: int,
        user_id: int,
        content_existed: bool = False,
    ) -> NovelMemo | None:
        """소설 메모를 조회합니다.

        Args:
            novel_id (int): 소설의 id입니다.
            user_id (int): 사용자의 id입니다.
            content_existed (bool, optional): 메모 내용이 있는지 여부입니다. Defaults to False.

        Returns:
            NovelMemo|None: 소설 메모 객체입니다.
        """
        stmt = select(NovelMemo).where(NovelMemo.novel_id == novel_id).where(NovelMemo.user_id == user_id)
        if content_existed:
            stmt = stmt.where(NovelMemo.content.is_not(None))
        return (await self.db.scalars(stmt)).first()

    async def get_memo_multi(
        self,
        user_id: int,
        novel_ids: Sequence[int] | None = None,
    ) -> Sequence[NovelMemo]:
        """소설 메모 목록을 조회합니다.

        Args:
            user_id (int): 사용자의 id입니다.
            novel_ids (list[int], optional): 소설의 id 목록입니다. Defaults to None.

        Returns:
            Sequence[NovelMemo]: 소설 메모 목록입니다.
        """
        stmt = select(NovelMemo).where(NovelMemo.user_id == user_id)
        if novel_ids:
            stmt = stmt.where(NovelMemo.novel_id.in_(novel_ids))
        return (await self.db.scalars(stmt)).all()

    async def create_memo(
        self,
        novel_id: int,
        user_id: int,
        content: str,
    ) -> NovelMemo:
        """소설 메모를 생성합니다.

        Args:
            novel_id (int): 소설의 id입니다.
            user_id (int): 사용자의 id입니다.
            content (str): 메모 내용입니다.

        Returns:
            NovelMemo: 소설 메모 객체입니다.
        """
        if not (novel_memo := await self.get_memo(novel_id, user_id)):
            novel_memo = NovelMemo(novel_id=novel_id, user_id=user_id)
        novel_memo.content = content
        novel_memo.modified_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        self.db.add(novel_memo)
        await self.db.flush()
        await self.db.refresh(novel_memo)
        return novel_memo

    async def delete_memo(
        self,
        novel_id: int,
        user_id: int,
    ) -> NovelMemo:
        """소설 메모를 삭제합니다.

        Args:
            novel_id (int): 소설의 id입니다.
            user_id (int): 사용자의 id입니다.

        Returns:
            NovelMemo: 소설 메모 객체입니다.
        """
        stmt = select(NovelMemo).where(NovelMemo.novel_id == novel_id, NovelMemo.user_id == user_id)
        novel_memo = (await self.db.scalars(stmt)).first()
        if not novel_memo:
            return
        novel_memo.content = None
        novel_memo.modified_at = None
        if not (novel_memo.content and novel_memo.average_star and novel_memo.is_favorite):
            await self.db.delete(novel_memo)
        else:
            self.db.add(novel_memo)
            await self.db.flush()
            await self.db.refresh(novel_memo)
        return novel_memo

    async def mark_as_favorite(
        self,
        novel_id: int,
        user_id: int,
    ) -> NovelMemo:
        """소설 메모를 즐겨찾기합니다.

        Args:
            novel_id (int): 소설의 id입니다.
            user_id (int): 사용자의 id입니다.

        Returns:
            NovelMemo: 소설 메모 객체입니다.
        """
        stmt = select(NovelMemo).where(NovelMemo.novel_id == novel_id, NovelMemo.user_id == user_id)
        novel_memo = (await self.db.scalars(stmt)).first()
        if not novel_memo:
            novel_memo = NovelMemo(novel_id=novel_id, user_id=user_id)
        novel_memo.is_favorite = True
        self.db.add(novel_memo)
        await self.db.flush()
        await self.db.refresh(novel_memo)
        return novel_memo

    async def unmark_as_favorite(
        self,
        novel_id: int,
        user_id: int,
    ) -> NovelMemo:
        """소설 메모를 즐겨찾기 해제합니다.

        Args:
            novel_id (int): 소설의 id입니다.
            user_id (int): 사용자의 id입니다.

        Returns:
            NovelMemo: 소설 메모 객체입니다.
        """
        stmt = select(NovelMemo).where(NovelMemo.novel_id == novel_id, NovelMemo.user_id == user_id)
        novel_memo = (await self.db.scalars(stmt)).first()
        if not novel_memo:
            return
        novel_memo.is_favorite = False
        if not (novel_memo.content and novel_memo.average_star and novel_memo.is_favorite):
            await self.db.delete(novel_memo)
        else:
            self.db.add(novel_memo)
            await self.db.flush()
            await self.db.refresh(novel_memo)
        return novel_memo

    async def update_average_star(
        self,
        novel_id: int,
        user_id: int,
    ) -> NovelMemo:
        """소설의 평균 별점을 업데이트합니다.

        Args:
            novel_id (int): 소설의 id입니다.
            user_id (int): 사용자의 id입니다.

        Returns:
            NovelMemo: 소설 메모 객체입니다.
        """
        stmt = select(NovelMemo).where(NovelMemo.novel_id == novel_id, NovelMemo.user_id == user_id)
        novel_memo = (await self.db.scalars(stmt)).first()
        if not novel_memo:
            novel_memo = NovelMemo(novel_id=novel_id, user_id=user_id)
        stmt = select(func.avg(ChapterMemo.star)).where(
            ChapterMemo.novel_id == novel_id, ChapterMemo.user_id == user_id, ChapterMemo.star.is_not(None)
        )
        average_star = await self.db.scalar(stmt)

        if average_star is None:
            return novel_memo
        novel_memo.average_star = round(average_star, 2)
        self.db.add(novel_memo)
        await self.db.flush()
        await self.db.refresh(novel_memo)
        return novel_memo


class CRUDChapter(CRUD[Chapter]):
    """소설 챕터 CRUD 클래스"""

    _order_columns = {
        ChapterOrder.CHAPTER_NO: Chapter.chapter_no,
    }

    async def get(
        self,
        novel_id: int,
        chapter_no: int,
    ) -> Chapter | None:
        """소설 챕터를 조회합니다.

        Args:
            novel_id (int): 소설의 id입니다.
            chapter_no (int): 챕터 번호입니다.

        Returns:
            Chapter|None: 소설 챕터 객체입니다.
        """
        stmt = select(Chapter).where(Chapter.novel_id == novel_id, Chapter.chapter_no == chapter_no)
        return (await self.db.scalars(stmt)).first()

    async def get_multi(
        self,
        novel_id: int,
        *,
        skip: int = 0,
        limit: int | None = None,
        order_by: ChapterOrder = ChapterOrder.CHAPTER_NO,
        desc: bool = True,
    ) -> Sequence[Chapter]:
        """소설 챕터 목록을 조회합니다.

        Args:
            novel_id (int): 소설의 id입니다.
            skip (int): 건너뛸 개수입니다. Defaults to 0.
            limit (int, optional): 최대 개수입니다. Defaults to None.
            order_by (ChapterOrder): 정렬 기준입니다. Defaults to ChapterOrder.CHAPTER_NO.
            desc (bool): 내림차순 여부입니다. Defaults to True.

        Returns:
            Sequence[Chapter]: 소설 챕터 목록입니다.
        """
        stmt = select(Chapter).where(Chapter.novel_id == novel_id)

        order_column = self._order_columns.get(order_by, Chapter.chapter_no)
        stmt = stmt.order_by(order_column.desc() if desc else order_column).offset(skip)

        if limit:
            stmt = stmt.limit(limit)

        return (await self.db.scalars(stmt)).all()

    async def get_memo_multi(
        self,
        novel_id: int,
        user_id: int,
        chapter_nos: Sequence[int] | None = None,
    ) -> Sequence[ChapterMemo]:
        """챕터 메모 목록을 조회합니다.

        Args:
            chapter_ids (list[int]): 챕터의 id 목록입니다.
            user_id (int): 사용자의 id입니다.
            chapter_nos (list[int], optional): 챕터 번호 목록입니다. Defaults to None.

        Returns:
            Sequence[ChapterMemo]: 챕터 메모 목록입니다.
        """
        stmt = select(ChapterMemo).where(ChapterMemo.novel_id == novel_id, ChapterMemo.user_id == user_id)
        if chapter_nos:
            stmt = stmt.where(ChapterMemo.chapter_no.in_(chapter_nos))
        return (await self.db.scalars(stmt)).all()

    async def get_memo(
        self,
        novel_id: int,
        chapter_no: int,
        user_id: int,
    ) -> ChapterMemo | None:
        """챕터 메모를 조회합니다.

        Args:
            novel_id (int): 소설의 id입니다.
            chapter_no (int): 챕터 번호입니다.
            user_id (int): 사용자의 id입니다.

        Returns:
            ChapterMemo|None: 챕터 메모 객체입니다.
        """
        stmt = select(ChapterMemo).where(
            ChapterMemo.novel_id == novel_id, ChapterMemo.chapter_no == chapter_no, ChapterMemo.user_id == user_id
        )
        return (await self.db.scalars(stmt)).first()

    async def create_memo(
        self,
        novel_id: int,
        chapter_no: int,
        user_id: int,
        content: str = None,
        star: int = None,
    ) -> ChapterMemo:
        """챕터 메모를 생성합니다.

        Args:
            novel_id (int): 소설의 id입니다.
            chapter_no (int): 챕터 번호입니다.
            user_id (int): 사용자의 id입니다.
            content (str, optional): 메모 내용입니다.
            star (int, optional): 별점입니다.

        Returns:
            ChapterMemo: 챕터 메모 객체입니다.
        """
        chapter_memo = ChapterMemo(
            novel_id=novel_id, chapter_no=chapter_no, user_id=user_id, content=content, star=star
        )
        self.db.add(chapter_memo)
        await self.db.flush()
        await self.db.refresh(chapter_memo)
        return chapter_memo

    async def update_memo(
        self,
        novel_id: int,
        chapter_no: int,
        user_id: int,
        content: str | None = None,
        star: int | None = None,
    ) -> ChapterMemo | None:
        """챕터 메모를 수정합니다.

        Args:
            novel_id (int): 소설의 id입니다.
            chapter_no (int): 챕터 번호입니다.
            user_id (int): 사용자의 id입니다.
            content (str, optional): 메모 내용입니다. Defaults to None.
            star (int, optional): 별점입니다. Defaults to None.

        Returns:
            ChapterMemo: 챕터 메모 객체입니다.
        """
        stmt = select(ChapterMemo).where(
            ChapterMemo.novel_id == novel_id, ChapterMemo.chapter_no == chapter_no, ChapterMemo.user_id == user_id
        )
        chapter_memo = (await self.db.scalars(stmt)).first()
        if not chapter_memo:
            return
        if content is not None:
            chapter_memo.content = content
        if star is not None:
            chapter_memo.star = star
        chapter_memo.modified_at = datetime.utcnow().replace(tzinfo=timezone.utc)
        self.db.add(chapter_memo)
        await self.db.flush()
        await self.db.refresh(chapter_memo)
        return chapter_memo

    async def delete_memo(
        self,
        novel_id: int,
        chapter_no: int,
        user_id: int,
    ) -> ChapterMemo:
        """챕터 메모를 삭제합니다.

        Args:
            novel_id (int): 소설의 id입니다.
            chapter_no (int): 챕터 번호입니다.
            user_id (int): 사용자의 id입니다.

        Returns:
            ChapterMemo: 챕터 메모 객체입니다.
        """
        stmt = select(ChapterMemo).where(
            ChapterMemo.novel_id == novel_id, ChapterMemo.chapter_no == chapter_no, ChapterMemo.user_id == user_id
        )

        if not (chapter_memo := (await self.db.scalars(stmt)).first()):
            return
        await self.db.delete(chapter_memo)

        return chapter_memo
