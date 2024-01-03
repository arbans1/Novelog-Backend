"""소설 관련 서비스를 제공합니다."""
import logging

import requests

from src.core.config import settings
from src.domain.novels.schemas import NovelCreate, NovelDTO
from src.libs.responses import NovelError

logger = logging.getLogger(__name__)


class NovelService:
    """소설 관련 서비스"""

    async def create(self, command: NovelCreate) -> NovelDTO:
        """소설을 생성합니다."""
        response = requests.post(
            settings.NOVEL_FETCH_URL, json=command.model_dump(mode="json", exclude_none=True), timeout=30
        )

        if response.status_code == 400:
            exception = NovelError.NOVEL_CREATE_FAILED.http_exception
            exception.detail = response.json()["detail"]
            raise exception

        if response.status_code == 404:
            raise NovelError.NOVEL_NOT_FOUND.http_exception

        if response.status_code != 200:
            logger.error("알 수 없는 이유로 소설 생성에 실패했습니다. %s %s", response.status_code, response.text)
            raise NovelError.UNEXPECTED_ERROR.http_exception

        return NovelDTO(**response.json())

    @classmethod
    @property
    def create_errors(cls) -> tuple:
        """에러 메시지"""
        return (
            NovelError.NOVEL_CREATE_FAILED,
            NovelError.NOVEL_NOT_FOUND,
            NovelError.UNEXPECTED_ERROR,
        )
