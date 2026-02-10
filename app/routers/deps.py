from fastapi import Depends, Header, HTTPException, status

from app.core.config import Settings, settings_dep
from app.db.session import SessionLocal


async def get_db():
    async with SessionLocal() as db:
        yield db


db_dep = Depends(get_db)


def verify_api_key(
    x_api_key: str | None = Header(None, alias="X-API-Key"),
    settings: Settings = settings_dep,
):
    if not x_api_key or x_api_key != settings.API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
