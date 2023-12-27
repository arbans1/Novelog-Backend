"""app에 대한 설정을 담고 있는 파일"""

import logging
from functools import lru_cache  # 가장 최근에 사용된 결과를 저장해두는 캐시

from pydantic import ConfigDict, Field, PostgresDsn, SecretStr, field_validator
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class StartSettings(BaseSettings):
    """환경변수를 읽어오는 클래스"""

    DEBUG: bool = Field(True, json_schema_extra={"env": "DEBUG"})


class CommonSettings(StartSettings):
    """
    환경변수를 읽어오는 클래스
    """

    PROJECT_NAME: str = "Novelog"

    JWT_ALGORITHM: str = "HS256"

    DB_PATH: PostgresDsn = Field(..., json_schema_extra={"env": "DB_PATH"})

    # AUTH
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int

    SECRET_KEY: SecretStr

    # CORS
    CORS_ORIGINS: list[str] = Field(..., json_schema_extra={"env": "CORS_ORIGINS"})

    @field_validator("DB_PATH", mode="before")
    @classmethod
    def check_db_path(cls, value: str):
        """PostgreSQL의 DB_PATH를 asyncpg의 DB_PATH로 변경합니다."""
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+asyncpg://")
        return value


class DevSettings(CommonSettings):
    """개발환경에서 사용하는 환경변수를 읽어오는 클래스"""

    model_config = ConfigDict(env_file=".env")

    # AUTH
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 1  # 1 day
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 day

    SECRET_KEY: SecretStr = SecretStr("secret")


class ProdSettings(CommonSettings):
    """운영환경에서 사용하는 환경변수를 읽어오는 클래스"""

    SECRET_KEY: SecretStr = Field(..., json_schema_extra={"env": "SECRET_KEY"})

    # AUTH
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # 15 minutes
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 day


@lru_cache  # 세팅같은 경우는 한번만 읽어오면 되므로 캐시를 사용
def get_settings():
    """환경변수를 읽어오는 함수"""
    if not StartSettings().DEBUG:
        return ProdSettings()
    logger.warning("Using dev settings. This is not intended for production.")
    return DevSettings()


settings = get_settings()
