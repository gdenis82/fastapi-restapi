import logging
import time

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import build_request_context, configure_logging, sanitize_value
from app.routers.buildings import router as buildings_router
from app.routers.deps import verify_api_key
from app.routers.organizations import router as organizations_router

configure_logging()
logger = logging.getLogger("app")

is_production = settings.ENVIRONMENT.lower() == "production"

docs_url = None if is_production else "/docs"
redoc_url = None if is_production else "/redoc"
openapi_url = None if is_production else f"{settings.API_V1_STR}/openapi.json"
app = FastAPI(title="Organizations Directory API",
              debug=not is_production,
              openapi_url=openapi_url,
              docs_url=docs_url,
              redoc_url=redoc_url,
              )

app.include_router(buildings_router)
app.include_router(organizations_router)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    start_time = time.monotonic()
    context = build_request_context(request)
    try:
        response = await call_next(request)
    except Exception as exc:
        duration_ms = (time.monotonic() - start_time) * 1000
        logger.error(
            "Request failed: %s %s -> exception=%s duration_ms=%.2f context=%s",
            request.method,
            request.url.path,
            type(exc).__name__,
            duration_ms,
            context,
        )
        raise
    duration_ms = (time.monotonic() - start_time) * 1000
    logger.info(
        "Request completed: %s %s -> %s duration_ms=%.2f context=%s",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        context,
    )
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    context = build_request_context(request)
    detail = sanitize_value(exc.detail)
    logger.warning(
        "HTTPException: status=%s detail=%s context=%s",
        exc.status_code,
        detail,
        context,
    )
    return JSONResponse(status_code=exc.status_code, content={"detail": detail}, headers=exc.headers)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    context = build_request_context(request)
    logger.exception("Unhandled exception: context=%s", context)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get(
    "/health",
    dependencies=[Depends(verify_api_key)],
    summary="Проверка доступности",
    description="Возвращает статус сервиса при корректном API ключе.",
)
def health_check():
    return {"status": "ok"}
