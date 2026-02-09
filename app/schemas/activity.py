from pydantic import BaseModel, ConfigDict


class ActivityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    parent_id: int | None
    depth: int