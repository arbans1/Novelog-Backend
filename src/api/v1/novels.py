"""소설 관련 API"""
# pylint: disable=redefined-builtin
from fastapi import APIRouter, Body, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from src.api import deps
from src.domain.novels.schemas import NovelCreate, NovelDTO, NovelsDTO, NovelsRequest
from src.domain.novels.service import NovelService
from src.libs.responses import UserError, get_error_response

router = APIRouter()


async def get_novel_service(db: Annotated[AsyncSession, Depends(deps.get_db)]) -> NovelService:
    """소설 서비스를 반환합니다."""
    return NovelService(db)


@router.post(
    "",
    response_model=NovelDTO,
    status_code=status.HTTP_201_CREATED,
    summary="플랫폼의 소설 id / url을 이용하여 소설을 등록합니다.",
    responses=get_error_response(NovelCreate.errors, NovelService.create_errors, UserError.CREDENTIALS_EXCEPTION),
    dependencies=[Depends(deps.get_token_payload)],
)
async def create_novel(
    novel_service: Annotated[NovelService, Depends(get_novel_service)],
    *,
    novel_create: Annotated[NovelCreate, Body(...)],
) -> NovelDTO:
    """플랫폼의 소설 id / url을 이용하여 소설을 등록합니다.(현재는 리디북스만 지원)"""
    return await novel_service.create(novel_create)


@router.get(
    "",
    response_model=NovelsDTO,
    summary="모든 소설을 조회합니다.",
    responses=get_error_response(),
)
async def get_novel_list(
    novel_service: Annotated[NovelService, Depends(get_novel_service)],
    *,
    novels_request: Annotated[NovelsRequest, Depends()],
) -> NovelsDTO:
    """모든 소설을 조회합니다."""
    return await novel_service.get_multi(novels_request)


@router.get(
    "/{novel_id}",
    response_model=NovelDTO,
    summary="특정 소설을 조회합니다.",
    responses=get_error_response(NovelService.get_errors),
)
async def get_novel(
    novel_service: Annotated[NovelService, Depends(get_novel_service)],
    *,
    novel_id: Annotated[int, Path(description="소설 ID")],
) -> NovelDTO:
    """특정 소설을 조회합니다."""
    return await novel_service.get(novel_id)
