from fastapi import Depends, FastAPI
from app.routers.buildings import router as buildings_router
from app.routers.deps import verify_api_key
from app.routers.organizations import router as organizations_router

app = FastAPI(title="Organizations Directory API")

app.include_router(buildings_router)
app.include_router(organizations_router)


@app.get(
    "/health",
    dependencies=[Depends(verify_api_key)],
    summary="Проверка доступности",
    description="Возвращает статус сервиса при корректном API ключе.",
)
def health_check():
    return {"status": "ok"}
