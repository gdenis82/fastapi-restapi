from pydantic import BaseModel, ConfigDict


class PhoneOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    number: str