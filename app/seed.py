import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import SessionLocal
from app.models.activity import Activity
from app.models.building import Building
from app.models.organization import Organization
from app.models.phone import Phone
async def seed():
    async with SessionLocal() as db:
        result = await db.scalars(select(Organization.id).limit(1))
        if result.first():
            return

        building1 = Building(address="г. Москва, ул. Ленина 1, офис 3", latitude=55.7558, longitude=37.6173)
        building2 = Building(address="г. Москва, ул. Блюхера 32/1", latitude=55.7702, longitude=37.6537)
        building3 = Building(address="г. Санкт-Петербург, Невский пр. 10", latitude=59.9343, longitude=30.3351)

        food = Activity(name="Еда", parent=None, depth=1)
        meat = Activity(name="Мясная продукция", parent=food, depth=2)
        dairy = Activity(name="Молочная продукция", parent=food, depth=2)

        auto = Activity(name="Автомобили", parent=None, depth=1)
        truck = Activity(name="Грузовые", parent=auto, depth=2)
        passenger = Activity(name="Легковые", parent=auto, depth=2)
        parts = Activity(name="Запчасти", parent=passenger, depth=3)
        accessories = Activity(name="Аксессуары", parent=passenger, depth=3)

        org1 = Organization(name="ООО Рога и Копыта", building=building2)
        org1.phones = [Phone(number="2-222-222"), Phone(number="3-333-333"), Phone(number="8-923-666-13-13")]
        org1.activities = [meat, dairy]

        org2 = Organization(name="Мясной Дом", building=building1)
        org2.phones = [Phone(number="8-800-100-00-01")]
        org2.activities = [meat]

        org3 = Organization(name="АвтоМир", building=building3)
        org3.phones = [Phone(number="8-812-111-22-33")]
        org3.activities = [passenger, accessories]

        org4 = Organization(name="ГрузПрофи", building=building1)
        org4.phones = [Phone(number="8-800-555-55-55")]
        org4.activities = [truck]

        db.add_all([building1, building2, building3])
        db.add_all([food, meat, dairy, auto, truck, passenger, parts, accessories])
        db.add_all([org1, org2, org3, org4])
        await db.commit()


if __name__ == "__main__":
    asyncio.run(seed())
