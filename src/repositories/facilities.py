from datetime import date

from src.models.facilities import FacilitiesOrm  # Модель, представляющая таблицу с комнатами (rooms)
from src.repositories.base import BaseRepository  # Базовый репозиторий, обеспечивающий базовые операции с БД
from src.repositories.utils import rooms_ids_for_booking
from src.schemas.facilities import Facilities  # Pydantic-схема для комнат


# Репозиторий для работы с комнатами (rooms)
class RoomsRepository(BaseRepository):
    # Связываем ORM-модель и Pydantic-схему с репозиторием
    model = FacilitiesOrm # Модель базы данных для таблицы rooms
    schema = Facilities  # Схема данных для сериализации комнат

    # Асинхронный метод для получения свободных комнат в заданный период времени
    async def get_filtered_by_time(
            self,
            title,
            hotel_id,  # ID отеля, для которого ищем комнаты

    ):
        # Подзапрос для подсчета количества занятых комнат по ID комнаты
        rooms_ids_to_get = rooms_ids_for_booking( hotel_id,)

        # Используем базовый метод get_filtered для фильтрации комнат
        # Здесь `RoomsORM.id.in_(rooms_ids_to_get)` добавляет условие на ID комнат
        return await self.F