from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from src.models.rooms import RoomsORM  # Модель, представляющая таблицу с комнатами (rooms)
from src.repositories.base import BaseRepository  # Базовый репозиторий, обеспечивающий базовые операции с БД
from src.repositories.mappers.mappers import RoomDataMapper, RoomDataWithRelsMapper
from src.repositories.utils import rooms_ids_for_booking


# Репозиторий для работы с комнатами (rooms)
class RoomsRepository(BaseRepository):
    # Связываем ORM-модель и Pydantic-схему с репозиторием
    model = RoomsORM  # Модель базы данных для таблицы rooms
    mapper = RoomDataMapper  # Схема данных для сериализации комнат

    # Асинхронный метод для получения свободных комнат в заданный период времени
    async def get_filtered_by_time(
            self,
            hotel_id,  # ID отеля, для которого ищем комнаты
            date_from: date,  # Дата начала периода
            date_to: date,  # Дата окончания периода
    ):
        # Подзапрос для подсчета количества занятых комнат по ID комнаты
        rooms_ids_to_get = rooms_ids_for_booking(date_from, date_to, hotel_id, )

        query = (
            select(self.model)
            .options(joinedload(self.model.facilities))
            .filter(RoomsORM.id.in_(rooms_ids_to_get))
        )
        result = await self.session.execute(query)
        return [RoomDataWithRelsMapper.map_to_domain_entity(model) for model in result.unique().scalars().all()]

    async def get_one_or_none_with_rels(self, **filter_by):
        query = (
            select(self.model)
            .options(selectinload(self.model.facilities))
            .filter_by(**filter_by)
        )
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        if model is None:
            return None
        return RoomDataWithRelsMapper.map_to_domain_entity(model)
