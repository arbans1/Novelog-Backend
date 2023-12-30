"""FastAPI 앱을 생성하고, API 라우터를 등록합니다."""
import json
from datetime import datetime

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from starlette.middleware.cors import CORSMiddleware

from src.api import router as api_router
from src.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,  # 프로젝트 이름을 설정합니다.
)


# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # CORS를 허용할 Origin을 설정합니다.
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드에 대해 CORS를 허용합니다.
    allow_headers=["*"],  # 모든 HTTP 헤더에 대해 CORS를 허용합니다.
)

if settings.DEBUG:

    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next: Response) -> Response:
        """
        요청마다 시작시간을 기록합니다.
        """
        request.state.start_time = datetime.now()
        response = await call_next(request)
        process_time = datetime.now() - request.state.start_time
        response.headers["X-Process-Time"] = f"{process_time.total_seconds():.4f}"
        return response

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler_debug(
        request: Request, exc: RequestValidationError  # pylint: disable=unused-argument
    ):
        """FastAPI의 RequestValidationError를 처리합니다."""
        exc_detail = json.dumps(exc.errors(), ensure_ascii=False)
        return JSONResponse({"detail": exc_detail}, status_code=status.HTTP_400_BAD_REQUEST)


if not settings.DEBUG:

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler_prod(
        request: Request, exc: RequestValidationError  # pylint: disable=unused-argument
    ):
        """FastAPI의 RequestValidationError를 처리합니다."""
        return JSONResponse({"detail": "잘못된 요청입니다."}, status_code=status.HTTP_400_BAD_REQUEST)


@app.get(
    "/health",
    summary="헬스체크용 API",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"description": "OK", "content": {"application/json": {"example": {"detail": "OK"}}}}
    },
    response_class=JSONResponse,
)
async def health():
    """헬스체크용 API"""
    return {"detail": "OK"}


app.include_router(api_router)
