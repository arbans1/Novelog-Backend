"""인증 서비스를 제공합니다."""
from fastapi import Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.security import create_jwt_token, decode_jwt_token, verify_password
from src.domain.auth.schemas import TokenDTO, TokenPayload
from src.domain.user.crud import CRUDUser
from src.libs.responses import UserError


class AuthService:
    """인증 서비스를 제공합니다."""

    def __init__(self, db: AsyncSession):
        self.crud_user = CRUDUser(db)

    async def authenticate(self, email: str, password: str) -> TokenPayload:
        """유저의 이메일과 비밀번호가 일치하는지 확인합니다."""
        user = await self.crud_user.get(email=email)
        credentials_exception = UserError.LOGIN_FAILED.http_exception
        credentials_exception.headers = {"WWW-Authenticate": "Bearer"}
        if not user or not verify_password(password, user.hashed_password):
            raise credentials_exception
        token_payload = TokenPayload(id=user.id, email=user.email)
        if user.is_admin:
            token_payload.is_admin = True
        if not user.is_active:
            token_payload.inactive = True
        return token_payload

    async def create_access_token(self, token_payload: TokenPayload) -> TokenDTO:
        """액세스 토큰을 생성합니다."""
        access_token = create_jwt_token(
            data=token_payload.model_dump(exclude_unset=True),
            expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )

        return TokenDTO(access_token=access_token, token_type="bearer")

    async def create_refresh_token(self, token_payload: TokenPayload, response: Response) -> Response:
        """리프레시 토큰을 생성합니다."""

        refresh_token = create_jwt_token(
            data=token_payload.model_dump(exclude_unset=True),
            expires_minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
        )
        response.set_cookie(
            key="refresh_token", value=refresh_token, httponly=True, max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60
        )
        return response

    async def refresh_access_token(self, request: Request) -> TokenPayload:
        """액세스 토큰을 재발급합니다."""
        token_payload = TokenPayload(**decode_jwt_token(request.cookies.get("refresh_token")))
        access_token = await self.create_access_token(token_payload)
        return access_token

    async def unset_refresh_token(self, response: Response) -> Response:
        """리프레시 토큰을 제거합니다."""
        response.delete_cookie(key="refresh_token")
        return response

    @classmethod
    @property
    def login_errors(cls) -> tuple:
        """로그인 관련 에러를 반환합니다."""
        return (UserError.LOGIN_FAILED,)

    @classmethod
    @property
    def token_errors(cls) -> tuple:
        """토큰 관련 에러를 반환합니다."""
        return (UserError.CREDENTIALS_EXCEPTION,)
