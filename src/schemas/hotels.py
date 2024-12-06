from pydantic import BaseModel, ConfigDict


class HotelAdd(BaseModel):
    title: str
    location: str


class Hotel(HotelAdd):
    id: int


class HotelPATCH(BaseModel):
    title: str | None = None
    location: str | None = None
