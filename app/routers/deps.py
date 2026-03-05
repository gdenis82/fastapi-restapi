from fastapi import Depends, Header, HTTPException, Query, status

from app.core.config import Settings, settings_dep
from app.db.session import SessionLocal
from app.schemas.common import PageParams


async def get_db():
    async with SessionLocal() as db:
        yield db


db_dep = Depends(get_db)


def pagination_dep(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
) -> PageParams:
    return PageParams(page=page, size=size)


def verify_api_key(
    x_api_key: str | None = Header(None, alias="X-API-Key"),
    settings: Settings = settings_dep,
):
    if not x_api_key or x_api_key not in settings.API_KEYS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
