import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings
from app.db.base import Base
from app.main import app
from app.models.activity import Activity
from app.models.building import Building
from app.models.organization import Organization
from app.models.phone import Phone
from app.routers.deps import get_db


@pytest.fixture
def auth_headers():
    return {"X-API-Key": "test-key"}


@pytest_asyncio.fixture
async def session_maker():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    yield session_factory
    await engine.dispose()


@pytest.fixture
def dependency_overrides():
    def _apply(overrides):
        app.dependency_overrides.update(overrides)

    yield _apply
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(session_maker, dependency_overrides):
    async def override_get_db():
        async with session_maker() as session:
            yield session

    def override_get_settings():
        base_settings = get_settings()
        return base_settings.model_copy(update={"API_KEY": "test-key"})

    dependency_overrides({get_db: override_get_db, get_settings: override_get_settings})
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def seed_data(session_maker):
    async with session_maker() as session:
        building1 = Building(address="Moscow, Lenina 1, office 3", latitude=55.7558, longitude=37.6173)
        building2 = Building(address="Moscow, Blyukhera 32/1", latitude=55.7702, longitude=37.6537)
        building3 = Building(address="Saint Petersburg, Nevsky 10", latitude=59.9343, longitude=30.3351)

        food = Activity(name="Food", parent=None, depth=1)
        meat = Activity(name="Meat", parent=food, depth=2)
        dairy = Activity(name="Dairy", parent=food, depth=2)

        auto = Activity(name="Auto", parent=None, depth=1)
        truck = Activity(name="Trucks", parent=auto, depth=2)

        org1 = Organization(name="Horns and Hooves LLC", building=building2)
        org1.phones = [Phone(number="2-222-222"), Phone(number="3-333-333")]
        org1.activities = [meat, dairy]

        org2 = Organization(name="Meat House", building=building1)
        org2.phones = [Phone(number="8-800-100-00-01")]
        org2.activities = [meat]

        org3 = Organization(name="AutoWorld", building=building3)
        org3.phones = [Phone(number="8-812-111-22-33")]
        org3.activities = [auto]

        org4 = Organization(name="TruckPro", building=building1)
        org4.phones = [Phone(number="8-800-555-55-55")]
        org4.activities = [truck]

        session.add_all([building1, building2, building3])
        session.add_all([food, meat, dairy, auto, truck])
        session.add_all([org1, org2, org3, org4])
        await session.flush()

        ids = {
            "buildings": {"b1": building1.id, "b2": building2.id, "b3": building3.id},
            "activities": {"food": food.id, "meat": meat.id, "auto": auto.id},
            "organizations": {"org1": org1.id, "org2": org2.id, "org3": org3.id, "org4": org4.id},
        }
        await session.commit()
        return ids
