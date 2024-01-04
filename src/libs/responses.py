"""반환값을 정의하는 모듈입니다."""
from collections import defaultdict
from enum import Enum
from functools import partial

from fastapi import HTTPException, status
from pydantic import BaseModel, Field
from typing_extensions import Annotated, Sequence

from src.libs.http_status_codes import STATUS_CODE_DESCRIPTION

__all__ = (
    "get_error_response",
    "UserError",
    "NovelError",
)


def get_error_response(
    *args: Enum | Sequence[Enum],
):
    """응답 메시지를 반환합니다.

    Args:
        *args (Enum): 에러 메시지

    Returns:
        dict: 응답 메시지
    """
    return_examples = defaultdict(list)
    for error_enum in args:
        if isinstance(error_enum, Enum):
            return_examples[error_enum.value.status_code].append(error_enum)
        else:
            for error in error_enum:
                return_examples[error.value.status_code].append(error)

    return {
        status_code: {
            "description": STATUS_CODE_DESCRIPTION[status_code],
            "content": {
                "application/json": {
                    "examples": {example.name: {"value": {"detail": str(example)}} for example in examples}
                }
            },
        }
        for status_code, examples in return_examples.items()
    }


class Error(BaseModel):
    """에러 메시지"""

    status_code: Annotated[int, Field(description="에러 상태 코드")]
    detail: Annotated[str, Field(description="에러 메시지")]

    def __str__(self):
        return str(self.detail)


class BaseError(Enum):
    """에러 메시지를 정의합니다."""

    def __str__(self):
        return str(self.value)

    @property
    def http_exception(self):
        """HTTP 예외를 반환합니다."""
        return HTTPException(status_code=self.value.status_code, detail=self.value.detail)


BadRequestError = partial(Error, status_code=status.HTTP_400_BAD_REQUEST)
UnauthorizedError = partial(Error, status_code=status.HTTP_401_UNAUTHORIZED)
ForbiddenError = partial(Error, status_code=status.HTTP_403_FORBIDDEN)
NotFoundError = partial(Error, status_code=status.HTTP_404_NOT_FOUND)
ConflictError = partial(Error, status_code=status.HTTP_409_CONFLICT)
UnprocessableEntityError = partial(Error, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
InternalServerError = partial(Error, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserError(BaseError):
    """사용자 관련 에러 메시지"""

    # 401
    LOGIN_FAILED = UnauthorizedError(detail="아이디 또는 비밀번호가 잘못되었습니다.")
    CREDENTIALS_EXCEPTION = UnauthorizedError(detail="자격 인증 정보가 유효하지 않습니다.")

    # 403
    FORBIDDEN = ForbiddenError(detail="권한이 없습니다.")

    # 404
    USER_NOT_FOUND = NotFoundError(detail="존재하지 않는 사용자입니다.")

    # 409
    EMAIL_ALREADY_EXISTS = ConflictError(detail="이미 등록된 이메일입니다.")
    NICKNAME_ALREADY_EXISTS = ConflictError(detail="이미 등록된 닉네임입니다.")

    # 422
    NICKNAME_TOO_SHORT = UnprocessableEntityError(detail="닉네임은 2자 이상이어야 합니다.")
    NICKNAME_TOO_LONG = UnprocessableEntityError(detail="닉네임은 10자 이하이어야 합니다.")
    NICKNAME_INVALID = UnprocessableEntityError(detail="닉네임에 사용할 수 없는 문자가 포함되어 있습니다.")

    PASSWORD_TOO_SHORT = UnprocessableEntityError(detail="비밀번호는 6자 이상이어야 합니다.")
    PASSWORD_TOO_LONG = UnprocessableEntityError(detail="비밀번호는 20자 이하이어야 합니다.")
    PASSWORD_MIX_REQUIRD = UnprocessableEntityError(detail="비밀번호에는 영문과 숫자가 모두 포함되어야 합니다.")


class NovelError(BaseError):
    """소설 관련 에러 메시지"""

    # 400
    NEED_NOVEL_REF = BadRequestError(detail="소설 ID 혹은 URL이 필요합니다.")
    NOVEL_CREATE_FAILED = BadRequestError(detail="소설 생성에 실패했습니다.")

    # 404
    NOVEL_NOT_FOUND = NotFoundError(detail="존재하지 않는 소설입니다.")

    # 409
    NOVEL_ALREADY_EXISTS = ConflictError(detail="이미 등록된 소설입니다.")

    # 500
    UNEXPECTED_ERROR = InternalServerError(detail="예상치 못한 에러가 발생했습니다.")
