import math

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import Select, and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, selectinload

from app.models.activity import Activity
from app.models.building import Building
from app.models.organization import Organization, organization_activity
from app.routers.deps import get_db, verify_api_key
from app.schemas.organization import OrganizationOut

router = APIRouter(prefix="/organizations", tags=["organizations"], dependencies=[Depends(verify_api_key)])


def _with_details(stmt: Select[tuple[Organization]]):
    return stmt.options(
        selectinload(Organization.building),
        selectinload(Organization.phones),
        selectinload(Organization.activities),
    )


async def _activity_descendants(session: AsyncSession, activity_id: int) -> list[int]:
    activity_cte = select(Activity.id).where(Activity.id == activity_id).cte(recursive=True)
    activity_alias = aliased(Activity)
    activity_cte = activity_cte.union_all(
        select(activity_alias.id).where(activity_alias.parent_id == activity_cte.c.id)
    )
    result = await session.execute(select(activity_cte.c.id))
    return [row[0] for row in result.all()]


@router.get(
    "/by-building/{building_id}",
    response_model=list[OrganizationOut],
    summary="Организации в здании",
    description="Возвращает все организации, находящиеся в указанном здании.",
)
async def list_by_building(building_id: int, db: AsyncSession = Depends(get_db)):
    stmt = _with_details(select(Organization).where(Organization.building_id == building_id))
    result = await db.scalars(stmt.order_by(Organization.id))
    return result.all()


@router.get(
    "/by-activity/{activity_id}",
    response_model=list[OrganizationOut],
    summary="Организации по деятельности",
    description="Возвращает организации, относящиеся к указанному виду деятельности.",
)
async def list_by_activity(activity_id: int, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Organization)
        .join(organization_activity)
        .where(organization_activity.c.activity_id == activity_id)
    )
    stmt = _with_details(stmt)
    result = await db.scalars(stmt.order_by(Organization.id))
    return result.all()


@router.get(
    "/by-activity-tree/{activity_id}",
    response_model=list[OrganizationOut],
    summary="Организации по дереву деятельности",
    description="Возвращает организации по виду деятельности и всем вложенным уровням.",
)
async def list_by_activity_tree(activity_id: int, db: AsyncSession = Depends(get_db)):
    activity_ids = await _activity_descendants(db, activity_id)
    if not activity_ids:
        return []
    stmt = (
        select(Organization)
        .join(organization_activity)
        .where(organization_activity.c.activity_id.in_(activity_ids))
        .distinct()
    )
    stmt = _with_details(stmt)
    result = await db.scalars(stmt.order_by(Organization.id))
    return result.all()


@router.get(
    "/by-activity-name",
    response_model=list[OrganizationOut],
    summary="Организации по названию деятельности",
    description="Ищет организации по названию деятельности. Можно включить вложенные уровни.",
)
async def list_by_activity_name(
    name: str = Query(..., min_length=1),
    include_children: bool = Query(True),
    db: AsyncSession = Depends(get_db),
):
    activity_result = await db.scalars(select(Activity).where(Activity.name == name))
    activity = activity_result.first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    activity_ids = [activity.id]
    if include_children:
        activity_ids = await _activity_descendants(db, activity.id)
    stmt = (
        select(Organization)
        .join(organization_activity)
        .where(organization_activity.c.activity_id.in_(activity_ids))
        .distinct()
    )
    stmt = _with_details(stmt)
    result = await db.scalars(stmt.order_by(Organization.id))
    return result.all()


@router.get(
    "/search",
    response_model=list[OrganizationOut],
    summary="Поиск организации по названию",
    description="Возвращает организации, название которых содержит указанную строку.",
)
async def search_by_name(name: str = Query(..., min_length=1), db: AsyncSession = Depends(get_db)):
    stmt = _with_details(select(Organization).where(Organization.name.ilike(f"%{name}%")))
    result = await db.scalars(stmt.order_by(Organization.id))
    return result.all()


@router.get(
    "/near",
    response_model=list[OrganizationOut],
    summary="Организации в радиусе",
    description="Возвращает организации, которые находятся в заданном радиусе от точки.",
)
async def list_nearby(
    lat: float = Query(...),
    lon: float = Query(...),
    radius_km: float = Query(..., gt=0),
    db: AsyncSession = Depends(get_db),
):
    lat_delta = radius_km / 111
    lon_delta = radius_km / (111 * max(math.cos(math.radians(lat)), 0.01))
    stmt = (
        select(Organization)
        .join(Building)
        .where(
            and_(
                (Building.latitude - lat).between(-lat_delta, lat_delta),
                (Building.longitude - lon).between(-lon_delta, lon_delta),
            )
        )
    )
    stmt = _with_details(stmt)
    result = await db.scalars(stmt.order_by(Organization.id))
    return result.all()


@router.get(
    "/within-rect",
    response_model=list[OrganizationOut],
    summary="Организации в прямоугольной области",
    description="Возвращает организации, чьи здания попадают в заданный прямоугольник.",
)
async def list_within_rect(
    min_lat: float = Query(...),
    max_lat: float = Query(...),
    min_lon: float = Query(...),
    max_lon: float = Query(...),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Organization)
        .join(Building)
        .where(
            and_(
                Building.latitude >= min_lat,
                Building.longitude >= min_lon,
                Building.latitude <= max_lat,
                Building.longitude <= max_lon,
            )
        )
    )
    stmt = _with_details(stmt)
    result = await db.scalars(stmt.order_by(Organization.id))
    return result.all()


@router.get(
    "/{organization_id}",
    response_model=OrganizationOut,
    summary="Информация об организации",
    description="Возвращает карточку организации по идентификатору.",
)
async def get_organization(organization_id: int, db: AsyncSession = Depends(get_db)):
    stmt = _with_details(select(Organization).where(Organization.id == organization_id))
    result = await db.scalars(stmt)
    organization = result.first()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization
