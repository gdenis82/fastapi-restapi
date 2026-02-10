import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import SessionLocal
from app.models.activity import Activity
from app.models.building import Building
from app.models.organization import Organization
from app.models.phone import Phone

BUILDING_DATA = {
    "b1": {"address": "г. Москва, ул. Ленина 1, офис 3", "latitude": 55.7558, "longitude": 37.6173},
    "b2": {"address": "г. Москва, ул. Блюхера 32/1", "latitude": 55.7702, "longitude": 37.6537},
    "b3": {"address": "г. Санкт-Петербург, Невский пр. 10", "latitude": 59.9343, "longitude": 30.3351},
    "b4": {"address": "г. Москва, ул. Тверская, д. 7", "latitude": 55.7579, "longitude": 37.6136},
    "b5": {"address": "г. Москва, ул. Арбат, д. 10", "latitude": 55.7496, "longitude": 37.5923},
    "b6": {"address": "г. Москва, Красная площадь, д. 1", "latitude": 55.7539, "longitude": 37.6208},
    "b7": {"address": "г. Москва, ул. Ленинские горы, д. 1", "latitude": 55.7020, "longitude": 37.5302},
    "b8": {"address": "г. Санкт-Петербург, Дворцовая пл., д. 2", "latitude": 59.9398, "longitude": 30.3146},
}

ACTIVITY_DATA = {
    "food": {"name": "Еда", "parent": None, "depth": 1},
    "meat": {"name": "Мясная продукция", "parent": "food", "depth": 2},
    "dairy": {"name": "Молочная продукция", "parent": "food", "depth": 2},
    "auto": {"name": "Автомобили", "parent": None, "depth": 1},
    "truck": {"name": "Грузовые", "parent": "auto", "depth": 2},
    "passenger": {"name": "Легковые", "parent": "auto", "depth": 2},
    "parts": {"name": "Запчасти", "parent": "passenger", "depth": 3},
    "accessories": {"name": "Аксессуары", "parent": "passenger", "depth": 3},
}

ORGANIZATION_DATA = {
    "org1": {
        "name": "ООО Рога и Копыта",
        "building": "b2",
        "phones": ["2-222-222", "3-333-333", "8-923-666-13-13"],
        "activities": ["meat", "dairy"],
    },
    "org2": {
        "name": "Мясной Дом",
        "building": "b1",
        "phones": ["8-800-100-00-01"],
        "activities": ["meat"],
    },
    "org3": {
        "name": "АвтоМир",
        "building": "b3",
        "phones": ["8-812-111-22-33"],
        "activities": ["passenger", "accessories"],
    },
    "org4": {
        "name": "ГрузПрофи",
        "building": "b1",
        "phones": ["8-800-555-55-55"],
        "activities": ["truck"],
    },
    "org5": {
        "name": "Тверская Еда",
        "building": "b4",
        "phones": ["8-495-111-22-33"],
        "activities": ["meat"],
    },
    "org6": {
        "name": "Арбат Кафе",
        "building": "b5",
        "phones": ["8-495-222-33-44"],
        "activities": ["dairy"],
    },
    "org7": {
        "name": "Молочная лавка",
        "building": "b1",
        "phones": ["8-495-333-44-55"],
        "activities": ["dairy"],
    },
    "org8": {
        "name": "Кремль Кафе",
        "building": "b6",
        "phones": ["8-495-444-55-66"],
        "activities": ["dairy"],
    },
    "org9": {
        "name": "Красная площадь Еда",
        "building": "b6",
        "phones": ["8-495-555-66-77"],
        "activities": ["meat"],
    },
    "org10": {
        "name": "Университетская столовая",
        "building": "b7",
        "phones": ["8-495-666-77-88"],
        "activities": ["dairy"],
    },
}


async def seed():
    async with SessionLocal() as db:
        result = await db.scalars(select(Organization.id).limit(1))
        if result.first():
            return

        buildings = {
            key: Building(
                address=data["address"],
                latitude=data["latitude"],
                longitude=data["longitude"],
            )
            for key, data in BUILDING_DATA.items()
        }

        activities = {
            key: Activity(name=data["name"], depth=data["depth"])
            for key, data in ACTIVITY_DATA.items()
        }
        for key, data in ACTIVITY_DATA.items():
            parent_key = data["parent"]
            if parent_key:
                activities[key].parent = activities[parent_key]

        organizations = {}
        for key, data in ORGANIZATION_DATA.items():
            org = Organization(name=data["name"], building=buildings[data["building"]])
            org.phones = [Phone(number=phone) for phone in data["phones"]]
            org.activities = [activities[activity_key] for activity_key in data["activities"]]
            organizations[key] = org

        db.add_all(buildings.values())
        db.add_all(activities.values())
        db.add_all(organizations.values())
        await db.commit()


if __name__ == "__main__":
    asyncio.run(seed())
