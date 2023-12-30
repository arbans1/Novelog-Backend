"""회원 관련 API"""
from fastapi import APIRouter, Body, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from src.api import deps
from src.domain.user.schemas import UserCreate, UserDTO
from src.domain.user.service import UserService
from src.libs.responses import get_error_response

router = APIRouter()


async def get_user_service(db: Annotated[AsyncSession, Depends(deps.get_db)]) -> UserService:
    """유저 서비스를 반환합니다."""
    return UserService(db)


@router.post(
    "",
    response_model=UserDTO,
    status_code=status.HTTP_201_CREATED,
    summary="회원을 생성합니다.",
    responses=get_error_response(*UserCreate.errors + UserDTO.errors + UserService.create_errors),
)
async def create_user(
    user_service: Annotated[UserService, Depends(get_user_service)],
    *,
    user_create: Annotated[UserCreate, Body(...)],
) -> UserDTO:
    """회원을 생성합니다."""
    return await user_service.create(user_create)
