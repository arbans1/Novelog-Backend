"""토큰 DTO 정의"""
from pydantic import ConfigDict

from src.domain.base.schemas import DTO

__all__ = ("TokenDTO", "TokenPayload")


class TokenDTO(DTO):
    """Access token schema."""

    access_token: str
    token_type: str


class TokenPayload(DTO):
    """Token payload schema."""

    model_config = ConfigDict(extra="ignore")

    id: int
    email: str
    is_admin: bool | None = None
    inactive: bool | None = None
