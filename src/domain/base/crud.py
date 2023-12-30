"""CRUD의 베이스 클래스를 정의한 모듈입니다."""

from abc import ABCMeta
from typing import Generic

from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.base.models import Model

__all__ = ("CRUD",)


class CRUD(Generic[Model], metaclass=ABCMeta):
    """CRUD의 베이스 클래스입니다."""

    def __init__(self, db: AsyncSession):
        """CRUD 생성자

        Args:
            db (AsyncSession): AsyncSession 객체입니다.
        """
        self.db = db

    async def save(self, model: Model) -> Model:
        """insert 혹은 update를 수행합니다.

        Args:
            model (Model): 저장할 객체입니다.
        """
        self.db.add(model)
        await self.db.flush()
        await self.db.refresh(model)
        return model
