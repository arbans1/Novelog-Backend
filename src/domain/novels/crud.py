"""소설 CRUD 관련 모듈입니다."""
# pylint: disable=redefined-builtin,too-many-arguments
from sqlalchemy import or_, select
from typing_extensions import Sequence

from src.domain.base.crud import CRUD
from src.domain.novels.models import Novel, NovelCategory
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
