import math

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.building import Building
from app.routers.deps import db_dep, pagination_dep, verify_api_key
from app.schemas.building import BuildingOut
from app.schemas.common import PageParams, PaginatedResponse

router = APIRouter(prefix="/buildings", tags=["buildings"], dependencies=[Depends(verify_api_key)])


@router.get(
    "",
    response_model=PaginatedResponse[BuildingOut],
    summary="Список зданий",
    description="Возвращает все здания из справочника.",
)
async def list_buildings(
    db: AsyncSession = db_dep,
    pagination: PageParams = Depends(pagination_dep),
):
    count_stmt = select(func.count()).select_from(Building)
    total = await db.scalar(count_stmt) or 0

    stmt = select(Building).order_by(Building.id)
    stmt = stmt.limit(pagination.size).offset((pagination.page - 1) * pagination.size)
    result = await db.scalars(stmt)
    items = list(result.all())

    return PaginatedResponse(
        items=items,
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=math.ceil(total / pagination.size) if total > 0 else 0,
    )
