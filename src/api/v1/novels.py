"""소설 관련 API"""
from fastapi import APIRouter, Body, Depends, status
from typing_extensions import Annotated

from src.api.deps import get_token_payload
from src.domain.novels.schemas import NovelCreate, NovelDTO
from src.domain.novels.service import NovelService
from src.libs.responses import UserError, get_error_response

router = APIRouter()


@router.post(
    "",
    response_model=NovelDTO,
    status_code=status.HTTP_201_CREATED,
    summary="소설을 생성합니다.",
    responses=get_error_response(NovelCreate.errors, NovelService.create_errors, UserError.CREDENTIALS_EXCEPTION),
    dependencies=[Depends(get_token_payload)],
)
async def create_novel(
    novel_service: Annotated[NovelService, Depends(NovelService)],
    *,
    novel_create: Annotated[NovelCreate, Body(...)],
) -> NovelDTO:
    """소설을 생성합니다."""
    return await novel_service.create(novel_create)
