from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.building import Building
from app.routers.deps import db_dep, verify_api_key
from app.schemas.building import BuildingOut

router = APIRouter(prefix="/buildings", tags=["buildings"], dependencies=[Depends(verify_api_key)])


@router.get(
    "",
    response_model=list[BuildingOut],
    summary="Список зданий",
    description="Возвращает все здания из справочника.",
)
async def list_buildings(db: AsyncSession = db_dep):
    result = await db.scalars(select(Building).order_by(Building.id))
    return result.all()
