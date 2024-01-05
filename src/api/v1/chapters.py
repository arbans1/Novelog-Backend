"""소설 챕터 관련 API"""
# pylint: disable=redefined-builtin
from fastapi import APIRouter, Body, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from src.api import deps
from src.domain.auth.schemas import TokenPayload
from src.domain.novels.schemas import (
    ChapterDTO,
    ChapterMemoContent,
    ChapterMemoContentNull,
    ChapterMemoCreate,
    ChapterMemoDTO,
    ChapterMemoUpdate,
    ChaptersDTO,
    ChaptersRequest,
)
from src.domain.novels.service import ChapterService, NovelService
from src.libs.responses import UserError, get_error_response

router = APIRouter()


async def get_chapter_service(db: Annotated[AsyncSession, Depends(deps.get_db)]) -> ChapterService:
    """챕터 서비스를 반환합니다."""
    return ChapterService(db)


@router.get(
    "",
    response_model=ChaptersDTO,
    summary="특정 소설의 챕터 목록을 조회합니다.",
    responses=get_error_response(NovelService.get_errors),
)
async def get_novel_chapters(
    chapter_service: Annotated[ChapterService, Depends(get_chapter_service)],
    novel_id: Annotated[int, Query(description="소설 ID")],
    *,
    chapters_request: Annotated[ChaptersRequest, Depends()],
) -> ChaptersDTO:
    """특정 소설의 챕터 목록을 조회합니다."""
    return await chapter_service.get_multi(novel_id, chapters_request)


@router.get(
    "/{chapter_id}",
    response_model=ChapterDTO,
    summary="특정 소설의 특정 회차를 조회합니다.",
    responses=get_error_response(ChapterService.get_errors),
)
async def get_novel_chapter(
    chapter_service: Annotated[ChapterService, Depends(get_chapter_service)],
    chapter_id: Annotated[int, Path(description="챕터 아이디")],
) -> ChapterDTO:
    """특정 소설의 특정 회차를 조회합니다."""
    return await chapter_service.get(chapter_id)


@router.get(
    "/{chapter_id}/memo",
    response_model=ChapterMemoDTO,
    summary="특정 회차에 등록된 메모 및 별점을 조회합니다.",
    responses=get_error_response(ChapterService.get_memo_errors),
)
async def get_novel_chapter_memo(
    chapter_service: Annotated[ChapterService, Depends(get_chapter_service)],
    chapter_id: Annotated[int, Path(description="챕터 아이디")],
    token: Annotated[TokenPayload, Depends(deps.get_token_payload)],
) -> ChapterMemoDTO:
    """특정 회차에 등록된 메모 및 별점을 조회합니다."""
    return await chapter_service.get_memo(chapter_id, token.id)


@router.post(
    "/{chapter_id}/memo",
    response_model=ChapterMemoDTO,
    summary="특정 회차에 메모 및 별점을 등록합니다.",
    responses=get_error_response(ChapterService.create_memo_errors, UserError.CREDENTIALS_EXCEPTION),
)
async def create_novel_chapter_memo(
    chapter_service: Annotated[ChapterService, Depends(get_chapter_service)],
    chapter_id: Annotated[int, Path(description="챕터 아이디")],
    token: Annotated[TokenPayload, Depends(deps.get_token_payload)],
    *,
    chapter_memo_content: Annotated[ChapterMemoContent, Body(...)],
) -> ChapterMemoDTO:
    """특정 회차에 메모 및 별점을 등록합니다."""
    chapter_memo_create = ChapterMemoCreate(
        **chapter_memo_content.model_dump(), chapter_id=chapter_id, user_id=token.id
    )
    return await chapter_service.create_memo(chapter_memo_create)


@router.patch(
    "/{chapter_id}/memo",
    response_model=ChapterMemoDTO,
    summary="특정 회차에 등록된 메모 및 별점을 수정합니다.",
    responses=get_error_response(ChapterService.get_memo_errors, UserError.CREDENTIALS_EXCEPTION),
)
async def update_novel_chapter_memo(
    chapter_service: Annotated[ChapterService, Depends(get_chapter_service)],
    chapter_id: Annotated[int, Path(description="챕터 아이디")],
    token: Annotated[TokenPayload, Depends(deps.get_token_payload)],
    *,
    chapter_memo_content: Annotated[ChapterMemoContentNull, Body(...)],
) -> ChapterMemoDTO:
    """특정 회차에 등록된 메모 및 별점을 수정합니다."""
    chapter_memo_update = ChapterMemoUpdate(
        **chapter_memo_content.model_dump(), chapter_id=chapter_id, user_id=token.id
    )
    return await chapter_service.update_memo(chapter_memo_update)


@router.delete(
    "/{chapter_id}/memo",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="특정 회차에 등록된 메모 및 별점을 삭제합니다.",
    responses=get_error_response(ChapterService.get_memo_errors, UserError.CREDENTIALS_EXCEPTION),
)
async def delete_novel_chapter_memo(
    chapter_service: Annotated[ChapterService, Depends(get_chapter_service)],
    chapter_id: Annotated[int, Path(description="챕터 아이디")],
    token: Annotated[TokenPayload, Depends(deps.get_token_payload)],
) -> None:
    """특정 회차에 등록된 메모 및 별점을 삭제합니다."""
    await chapter_service.delete_memo(chapter_id, token.id)
