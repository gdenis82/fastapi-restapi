from pydantic import BaseModel, ConfigDict

from app.schemas.activity import ActivityOut
from app.schemas.building import BuildingOut
from app.schemas.phone import PhoneOut


class OrganizationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    building: BuildingOut
    phones: list[PhoneOut]
    activities: list[ActivityOut]