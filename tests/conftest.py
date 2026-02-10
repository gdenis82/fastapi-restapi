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
        building_data = {
            "b1": {"address": "Moscow, Lenina 1, office 3", "latitude": 55.7558, "longitude": 37.6173},
            "b2": {"address": "Moscow, Blyukhera 32/1", "latitude": 55.7702, "longitude": 37.6537},
            "b3": {"address": "Saint Petersburg, Nevsky 10", "latitude": 59.9343, "longitude": 30.3351},
            "b4": {"address": "Moscow, Tverskaya 7", "latitude": 55.7579, "longitude": 37.6136},
            "b5": {"address": "Moscow, Arbat 10", "latitude": 55.7496, "longitude": 37.5923},
            "b6": {"address": "Moscow, Red Square 1", "latitude": 55.7539, "longitude": 37.6208},
            "b7": {"address": "Moscow, Leninskie Gory 1", "latitude": 55.7020, "longitude": 37.5302},
            "b8": {"address": "Saint Petersburg, Palace Sq 2", "latitude": 59.9398, "longitude": 30.3146},
        }

        activity_data = {
            "food": {"name": "Food", "parent": None, "depth": 1},
            "meat": {"name": "Meat", "parent": "food", "depth": 2},
            "dairy": {"name": "Dairy", "parent": "food", "depth": 2},
            "auto": {"name": "Auto", "parent": None, "depth": 1},
            "truck": {"name": "Trucks", "parent": "auto", "depth": 2},
        }

        organization_data = {
            "org1": {
                "name": "Horns and Hooves LLC",
                "building": "b2",
                "phones": ["2-222-222", "3-333-333"],
                "activities": ["meat", "dairy"],
            },
            "org2": {
                "name": "Meat House",
                "building": "b1",
                "phones": ["8-800-100-00-01"],
                "activities": ["meat"],
            },
            "org3": {
                "name": "AutoWorld",
                "building": "b3",
                "phones": ["8-812-111-22-33"],
                "activities": ["auto"],
            },
            "org4": {
                "name": "TruckPro",
                "building": "b1",
                "phones": ["8-800-555-55-55"],
                "activities": ["truck"],
            },
            "org5": {
                "name": "Tverskaya Food",
                "building": "b4",
                "phones": ["8-495-111-22-33"],
                "activities": ["meat"],
            },
            "org6": {
                "name": "Arbat Cafe",
                "building": "b5",
                "phones": ["8-495-222-33-44"],
                "activities": ["dairy"],
            },
            "org7": {
                "name": "Milk Market",
                "building": "b1",
                "phones": ["8-495-333-44-55"],
                "activities": ["dairy"],
            },
            "org8": {
                "name": "Kremlin Cafe",
                "building": "b6",
                "phones": ["8-495-444-55-66"],
                "activities": ["dairy"],
            },
            "org9": {
                "name": "Red Square Food",
                "building": "b6",
                "phones": ["8-495-555-66-77"],
                "activities": ["meat"],
            },
            "org10": {
                "name": "University Canteen",
                "building": "b7",
                "phones": ["8-495-666-77-88"],
                "activities": ["dairy"],
            },
        }

        buildings = {
            key: Building(
                address=data["address"],
                latitude=data["latitude"],
                longitude=data["longitude"],
            )
            for key, data in building_data.items()
        }

        activities = {
            key: Activity(name=data["name"], depth=data["depth"])
            for key, data in activity_data.items()
        }
        for key, data in activity_data.items():
            parent_key = data["parent"]
            if parent_key:
                activities[key].parent = activities[parent_key]

        organizations = {}
        for key, data in organization_data.items():
            org = Organization(name=data["name"], building=buildings[data["building"]])
            org.phones = [Phone(number=phone) for phone in data["phones"]]
            org.activities = [activities[activity_key] for activity_key in data["activities"]]
            organizations[key] = org

        session.add_all(buildings.values())
        session.add_all(activities.values())
        session.add_all(organizations.values())
        await session.flush()

        ids = {
            "buildings": {key: building.id for key, building in buildings.items()},
            "activities": {key: activity.id for key, activity in activities.items()},
            "organizations": {key: org.id for key, org in organizations.items()},
        }
        await session.commit()
        return ids
