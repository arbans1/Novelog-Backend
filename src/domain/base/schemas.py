"""DTO를 담당하는 기본 클래스를 정의합니다."""

from abc import ABC

from pydantic import BaseModel, ConfigDict

__all__ = ("Base", "DTO")


class Base(BaseModel, ABC):
    """DTO를 담당하는 기본 클래스입니다."""

    @classmethod
    @property
    def errors(cls) -> tuple:
        """에러 메시지"""
        return ()


class DTO(Base, ABC):
    """DTO를 담당하는 기본 클래스입니다."""

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    @property
    def errors(cls) -> tuple:
        """에러 메시지"""
        return ()
