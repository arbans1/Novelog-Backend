"""유효성 검사 모듈"""
from src.domain.base.validators import Validator
from src.libs.responses import UserError

__all__ = (
    "NickNameValidator",
    "PasswordValidator",
)

INVALID_CHARACTERS = (" ", "'", '"', "<", ">", ";", "&", "#", "!", "?", "|", "/", "\\", "*", ":", "@")
INVALID_NICKNAMES = ("admin", "administrator", "root", "superuser", "supervisor", "운영자", "관리자", "시스템", "시스템관리자")


class NickNameValidator(Validator):
    """닉네임 유효성 검사"""

    @classmethod
    @property
    def errors(cls) -> tuple:
        """에러 메시지"""
        return (
            UserError.NICKNAME_TOO_SHORT,
            UserError.NICKNAME_TOO_LONG,
            UserError.NICKNAME_INVALID,
        )

    def __call__(self, nickname: str) -> str:
        """닉네임 유효성 검사"""
        if nickname in INVALID_NICKNAMES or any(character in nickname for character in INVALID_CHARACTERS):
            raise UserError.NICKNAME_INVALID.http_exception
        if len(nickname) < 2:
            raise UserError.NICKNAME_TOO_SHORT.http_exception
        if len(nickname) > 10:
            raise UserError.NICKNAME_TOO_LONG.http_exception
        return nickname


class PasswordValidator(Validator):
    """비밀번호 유효성 검사"""

    @classmethod
    @property
    def errors(cls) -> tuple:
        """에러 메시지"""
        return (
            UserError.PASSWORD_TOO_SHORT,
            UserError.PASSWORD_TOO_LONG,
            UserError.PASSWORD_MIX_REQUIRD,
        )

    def __call__(self, password: str) -> str:
        """비밀번호 유효성 검사"""
        if len(password) < 6:
            raise UserError.PASSWORD_TOO_SHORT.http_exception
        if len(password) > 20:
            raise UserError.PASSWORD_TOO_LONG.http_exception
        if not (
            any(character.isdigit() for character in password) and any(character.isalpha() for character in password)
        ):
            raise UserError.PASSWORD_MIX_REQUIRD.http_exception
        return password
