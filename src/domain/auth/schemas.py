"""토큰 DTO 정의"""
from pydantic import ConfigDict, EmailStr, Field
from typing_extensions import Annotated

from src.domain.base.schemas import DTO

__all__ = ("TokenDTO", "TokenPayload")


class TokenDTO(DTO):
    """Access token schema."""

    access_token: Annotated[str, Field(description="Access token")]
    token_type: Annotated[str, Field(description="Token type")]


class TokenPayload(DTO):
    """Token payload schema."""

    model_config = ConfigDict(extra="ignore")

    id: Annotated[int, Field(description="유저 ID")]
    email: Annotated[EmailStr, Field(description="이메일")]
    is_admin: Annotated[bool | None, Field(description="관리자 여부")] = None
    inactive: Annotated[bool | None, Field(description="비활성 유저 여부")] = None
