from pydantic import BaseModel, ConfigDict
from typing import Optional


class RoomAdd(BaseModel):
    title: str
    description: Optional[str] = None


class Room(RoomAdd):
    id: int
    hotel_id: int

    model_config = ConfigDict(from_attributes=True)
