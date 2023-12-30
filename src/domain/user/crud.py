"""유저 CRUD 관련 모듈입니다."""
# pylint: disable=redefined-builtin
from sqlalchemy import or_, select

from src.domain.base.crud import CRUD
from src.domain.user.models import User


class CRUDUser(CRUD[User]):
    """유저 CRUD 클래스"""

    async def get(self, id: int | None = None, email: str | None = None, nickname: str | None = None) -> User | None:
        """유저를 조회합니다. 여러 조건을 입력하면 or 조건으로 조회합니다.

        Args:
            id (int, optional): 유저의 id입니다. Defaults to None.
            email (str, optional): 유저의 이메일입니다. Defaults to None.
            nickname (str, optional): 유저의 닉네임입니다. Defaults to None.

        Returns:
            User|None: 유저 객체입니다.
        """
        assert id or email or nickname, "id, email, nickname 중 하나는 필수로 입력해야 합니다."
        stmt = select(User)

        or_conditions = []
        if id:
            or_conditions.append(User.id == id)
        if email:
            or_conditions.append(User.email == email)
        if nickname:
            or_conditions.append(User.nickname == nickname)

        stmt = stmt.where(or_(*or_conditions))
        return (await self.db.scalars(stmt)).first()
