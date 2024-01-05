"""소설 CRUD 관련 모듈입니다."""
# pylint: disable=redefined-builtin,too-many-arguments
from datetime import datetime, timezone

from sqlalchemy import or_, select
from typing_extensions import Sequence

from src.domain.base.crud import CRUD
from src.domain.novels.models import Novel, NovelCategory, NovelMemo
from src.domain.novels.schemas import NovelCategoryFilter, NovelFilter, NovelOrder, Platform


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
