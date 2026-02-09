from fastapi import Header, HTTPException, status
from app.core.config import settings
from app.db.session import SessionLocal


async def get_db():
    async with SessionLocal() as db:
        yield db


def verify_api_key(x_api_key: str | None = Header(None, alias="X-API-Key")):
    if not x_api_key or x_api_key != settings.api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
