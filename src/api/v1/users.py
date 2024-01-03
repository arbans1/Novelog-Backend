"""회원 관련 API"""
from fastapi import APIRouter, Body, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from src.api import deps
from src.domain.auth.schemas import TokenPayload
from src.domain.auth.service import AuthService
from src.domain.users.schemas import UserCreate, UserDTO
from src.domain.users.service import UserService
from src.libs.responses import get_error_response

router = APIRouter()


async def get_user_service(db: Annotated[AsyncSession, Depends(deps.get_db)]) -> UserService:
    """유저 서비스를 반환합니다."""
    return UserService(db)


async def get_auth_service(db: Annotated[AsyncSession, Depends(deps.get_db)]) -> AuthService:
    """인증 서비스를 반환합니다."""
    return AuthService(db)


@router.post(
    "",
    response_model=UserDTO,
    status_code=status.HTTP_201_CREATED,
    summary="회원을 생성합니다.",
    responses=get_error_response(UserCreate.errors, UserDTO.errors, UserService.create_errors),
)
async def create_user(
    user_service: Annotated[UserService, Depends(get_user_service)],
    *,
    user_create: Annotated[UserCreate, Body(...)],
) -> UserDTO:
    """회원을 생성합니다."""
    return await user_service.create(user_create)


@router.get(
    "/me",
    response_model=UserDTO,
    summary="내 정보를 반환합니다.",
    responses=get_error_response(UserDTO.errors, UserService.get_errors),
)
async def get_me(
    user_service: Annotated[UserService, Depends(get_user_service)],
    token: Annotated[TokenPayload, Depends(deps.get_token_payload)],
) -> UserDTO:
    """내 정보를 반환합니다."""
    return await user_service.get(id=token.id)


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="내 정보를 삭제합니다.",
    responses=get_error_response(AuthService.token_errors, UserService.get_errors),
)
async def delete_me(
    response: Response,
    user_service: Annotated[UserService, Depends(get_user_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    token: Annotated[TokenPayload, Depends(deps.get_token_payload)],
) -> None:
    """내 정보를 삭제합니다."""
    await user_service.delete(token.id)
    await auth_service.unset_refresh_token(response)
