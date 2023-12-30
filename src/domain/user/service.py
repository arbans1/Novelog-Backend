"""유저 관련 서비스를 제공합니다."""
# pylint: disable=redefined-builtin
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import get_password_hash
from src.domain.base.service import to_dto
from src.domain.user.crud import CRUDUser
from src.domain.user.models import User
from src.domain.user.schemas import UserCreate, UserDTO
from src.libs.responses import UserError

__all__ = ("UserService",)


@to_dto.register(User)
def _(obj: User) -> UserDTO:
    """User 객체를 UserDTO 객체로 변환합니다."""
    return UserDTO.model_validate(obj)


class UserService:
    """유저 서비스를 제공합니다."""

    def __init__(self, db: AsyncSession):
        self.crud_user = CRUDUser(db)

    async def get(self, id: int | None = None, email: str | None = None, nickname: str | None = None) -> UserDTO | None:
        """유저를 조회합니다. 여러 조건을 입력하면 or 조건으로 조회합니다.

        Args:
            id (int, optional): 유저의 id입니다. Defaults to None.
            email (str, optional): 유저의 이메일입니다. Defaults to None.
            nickname (str, optional): 유저의 닉네임입니다. Defaults to None.

        Returns:
            UserDto: 유저 DTO입니다.
        """
        user = await self.crud_user.get(id, email, nickname)
        if user:
            return to_dto(user)
        raise UserError.USER_NOT_FOUND.http_exception

    async def create(self, command: UserCreate) -> UserDTO:
        """회원 정보(이메일, 닉네임, 생년월일)를 등록한다."""
        existing_user = await self.get(email=command.email, nickname=command.nickname)
        if existing_user and existing_user.email == command.email:
            raise UserError.EMAIL_ALREADY_EXISTS.http_exception
        if existing_user and existing_user.nickname == command.nickname:
            raise UserError.NICKNAME_ALREADY_EXISTS.http_exception

        model = User(
            email=command.email,
            nickname=command.nickname,
            hashed_password=get_password_hash(command.password),
            is_admin=False,
            is_active=True,
        )
        return to_dto(await self.crud_user.save(model))

    async def delete(self, id: int) -> None:
        """유저를 삭제합니다."""
        if not await self.crud_user.delete(id):
            raise UserError.USER_NOT_FOUND.http_exception

    @classmethod
    @property
    def create_errors(cls) -> tuple:
        """에러 메시지를 반환합니다."""
        return (
            UserError.EMAIL_ALREADY_EXISTS,
            UserError.NICKNAME_ALREADY_EXISTS,
        )

    @classmethod
    @property
    def get_errors(cls) -> tuple:
        """에러 메시지를 반환합니다."""
        return (UserError.USER_NOT_FOUND,)
