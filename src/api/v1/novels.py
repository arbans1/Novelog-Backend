"""소설 관련 API"""
# pylint: disable=redefined-builtin
from fastapi import APIRouter, Body, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from src.api import deps
from src.domain.auth.schemas import TokenPayload
from src.domain.novels.schemas import (
    NovelCreate,
    NovelDTO,
    NovelMemoContent,
    NovelMemoCreate,
    NovelMemoDTO,
    NovelsDTO,
    NovelsRequest,
)
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
    novel_id: Annotated[int, Path(description="소설 ID")],
) -> NovelDTO:
    """특정 소설을 조회합니다."""
    return await novel_service.get(novel_id)


@router.get(
    "/{novel_id}/memo",
    response_model=NovelMemoDTO,
    summary="특정 소설의 메모를 조회합니다.",
    responses=get_error_response(UserError.CREDENTIALS_EXCEPTION),
)
async def get_novel_memo(
    novel_service: Annotated[NovelService, Depends(get_novel_service)],
    novel_id: Annotated[int, Path(description="소설 ID")],
    token: Annotated[TokenPayload, Depends(deps.get_token_payload)],
) -> NovelMemoDTO:
    """특정 소설의 메모를 조회합니다."""
    return await novel_service.get_memo(novel_id, token.id)


@router.post(
    "/{novel_id}/memo",
    response_model=NovelMemoDTO,
    status_code=status.HTTP_201_CREATED,
    summary="특정 소설에 메모를 등록합니다.",
    responses=get_error_response(NovelService.create_memo_errors, UserError.CREDENTIALS_EXCEPTION),
)
async def create_novel_memo(
    novel_service: Annotated[NovelService, Depends(get_novel_service)],
    novel_id: Annotated[int, Path(description="소설 ID")],
    token: Annotated[TokenPayload, Depends(deps.get_token_payload)],
    *,
    content: Annotated[NovelMemoContent, Body(...)],
) -> NovelMemoDTO:
    """특정 소설에 메모를 등록합니다."""
    novel_memo_create = NovelMemoCreate(novel_id=novel_id, user_id=token.id, content=content.content)
    return await novel_service.create_memo(novel_memo_create)


@router.patch(
    "/{novel_id}/memo",
    response_model=NovelMemoDTO,
    summary="특정 소설의 메모를 수정합니다.",
    responses=get_error_response(NovelService.update_memo_errors, UserError.CREDENTIALS_EXCEPTION),
)
async def update_novel_memo(
    novel_service: Annotated[NovelService, Depends(get_novel_service)],
    novel_id: Annotated[int, Path(description="소설 ID")],
    token: Annotated[TokenPayload, Depends(deps.get_token_payload)],
    *,
    content: Annotated[NovelMemoContent, Body(...)],
) -> NovelMemoDTO:
    """특정 소설의 메모를 수정합니다."""
    novel_memo_create = NovelMemoCreate(novel_id=novel_id, user_id=token.id, content=content.content)
    return await novel_service.update_memo(novel_memo_create)


@router.delete(
    "/{novel_id}/memo",
    response_model=NovelMemoDTO,
    status_code=status.HTTP_200_OK,
    summary="특정 소설의 메모를 삭제합니다.",
    responses=get_error_response(NovelService.update_memo_errors, UserError.CREDENTIALS_EXCEPTION),
)
async def delete_novel_memo(
    novel_service: Annotated[NovelService, Depends(get_novel_service)],
    novel_id: Annotated[int, Path(description="소설 ID")],
    token: Annotated[TokenPayload, Depends(deps.get_token_payload)],
) -> NovelMemoDTO:
    """특정 소설의 메모를 삭제합니다."""
    return await novel_service.delete_memo(novel_id, token.id)


@router.post(
    "/{novel_id}/favorites",
    response_model=NovelMemoDTO,
    status_code=status.HTTP_201_CREATED,
    summary="특정 소설을 즐겨찾기에 추가합니다.",
    responses=get_error_response(NovelService.update_memo_errors, UserError.CREDENTIALS_EXCEPTION),
)
async def mark_as_favorite(
    novel_service: Annotated[NovelService, Depends(get_novel_service)],
    novel_id: Annotated[int, Path(description="소설 ID")],
    token: Annotated[TokenPayload, Depends(deps.get_token_payload)],
) -> NovelMemoDTO:
    """특정 소설을 즐겨찾기에 추가합니다."""
    return await novel_service.mark_as_favorite(novel_id, token.id)


@router.delete(
    "/{novel_id}/favorites",
    response_model=NovelMemoDTO,
    status_code=status.HTTP_200_OK,
    summary="특정 소설을 즐겨찾기에서 제거합니다.",
    responses=get_error_response(NovelService.update_memo_errors, UserError.CREDENTIALS_EXCEPTION),
)
async def unmark_as_favorite(
    novel_service: Annotated[NovelService, Depends(get_novel_service)],
    novel_id: Annotated[int, Path(description="소설 ID")],
    token: Annotated[TokenPayload, Depends(deps.get_token_payload)],
) -> NovelMemoDTO:
    """특정 소설을 즐겨찾기에서 제거합니다."""
    return await novel_service.unmark_as_favorite(novel_id, token.id)
