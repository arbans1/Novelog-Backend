"""유저 DTO 정의"""

from pydantic import BeforeValidator, EmailStr, Field
from typing_extensions import Annotated

from src.domain.base.schemas import DTO, Base
from src.domain.users.validators import NickNameValidator, PasswordValidator

__all__ = (
    "UserDTO",
    "UserCreate",
)


NickName = Annotated[str, BeforeValidator(NickNameValidator())]
Password = Annotated[str, BeforeValidator(PasswordValidator())]


class UserBase(Base):
    """유저 기본 DTO"""

    email: Annotated[EmailStr, Field(description="이메일")]
    nickname: Annotated[NickName, Field(description="닉네임")]

    @classmethod
    @property
    def errors(cls) -> tuple:
        """에러 메시지"""
        return NickNameValidator.errors


class UserDTO(DTO, UserBase):
    """유저 DTO"""

    is_admin: Annotated[bool, Field(description="관리자 여부")]
    is_active: Annotated[bool, Field(description="활성화 여부")]

    @classmethod
    @property
    def errors(cls) -> tuple:
        """에러 메시지"""
        return super().errors


class UserCreate(UserBase):
    """유저 생성 DTO"""

    password: Annotated[Password, Field(description="비밀번호")]

    @classmethod
    @property
    def errors(cls) -> tuple:
        """에러 메시지"""
        return super().errors + PasswordValidator.errors
