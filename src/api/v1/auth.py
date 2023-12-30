"""인증 관련 API"""
from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from src.api import deps
from src.domain.auth.schemas import TokenDTO, TokenPayload
from src.domain.auth.service import AuthService
from src.libs.responses import get_error_response

router = APIRouter()


async def get_auth_service(db: Annotated[AsyncSession, Depends(deps.get_db)]) -> AuthService:
    """인증 서비스를 반환합니다."""
    return AuthService(db)


@router.post(
    "/login",
    response_model=TokenDTO,
    status_code=status.HTTP_200_OK,
    summary="로그인합니다.",
    responses=get_error_response(AuthService.login_errors),
)
async def login(
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    *,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> TokenDTO:
    """로그인합니다."""
    token_payload = await auth_service.authenticate(form_data.username, form_data.password)
    response = await auth_service.create_refresh_token(token_payload, response)
    return await auth_service.create_access_token(token_payload)


@router.post(
    "/refresh",
    response_model=TokenDTO,
    status_code=status.HTTP_200_OK,
    summary="액세스토큰을 재발급합니다.",
    responses=get_error_response(AuthService.token_errors),
)
async def refresh(
    request: Request,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenDTO:
    """액세스토큰을 재발급합니다."""
    return await auth_service.refresh_access_token(request)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="로그아웃합니다.",
)
async def logout(
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> Response:
    """로그아웃합니다."""
    await auth_service.unset_refresh_token(response)


@router.post(
    "/test",
    status_code=status.HTTP_200_OK,
    summary="토큰을 테스트합니다.",
    responses=get_error_response(AuthService.token_errors),
    response_model=TokenPayload,
    response_model_exclude_unset=True,
)
async def test(
    token: Annotated[TokenPayload, Depends(deps.get_token_payload)],
) -> TokenPayload:
    """토큰을 테스트합니다."""
    return token
