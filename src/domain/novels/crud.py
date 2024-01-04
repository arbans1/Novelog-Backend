"""소설 CRUD 관련 모듈입니다."""
# pylint: disable=redefined-builtin
from sqlalchemy import select

from src.domain.base.crud import CRUD
from src.domain.novels.models import Novel
from src.domain.novels.schemas import Platform


class CRUDNovel(CRUD[Novel]):
    """소설 CRUD 클래스"""

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
