from fastapi import Depends, FastAPI
from app.routers.deps import verify_api_key


app = FastAPI(title="Organizations Directory API")




@app.get(
    "/health",
    dependencies=[Depends(verify_api_key)],
    summary="Проверка доступности",
    description="Возвращает статус сервиса при корректном API ключе.",
)
def health_check():
    return {"status": "ok"}
