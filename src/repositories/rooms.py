from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.rooms import RoomsORM
from src.repositories.base import BaseRepository
from src.schemas.rooms import Room, RoomAdd
from typing import List


class RoomsRepository(BaseRepository):
    model = RoomsORM
    schema = Room

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.session = session  # Убедитесь, что у нас есть сессия для запросов

    async def get_all(self, hotel_id: int, limit: int, offset: int) -> List[Room]:
        """Получить все комнаты для отеля с указанным hotel_id."""
        query = select(self.model).where(self.model.hotel_id == hotel_id).limit(limit).offset(offset)
        result = await self.session.execute(query)
        rooms = result.scalars().all()
        return [self.schema.model_validate(room, from_attributes=True) for room in rooms] if rooms else []


