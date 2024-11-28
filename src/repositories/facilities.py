from src.models.facilities import FacilitiesOrm  # Модель, представляющая таблицу с комнатами (rooms)
from src.repositories.base import BaseRepository  # Базовый репозиторий, обеспечивающий базовые операции с БД
from src.schemas.facilities import Facility  # Pydantic-схема для комнат


# Репозиторий для работы с комнатами (rooms)
class FacilitiesRepository(BaseRepository):
    # Связываем ORM-модель и Pydantic-схему с репозиторием
    model = FacilitiesOrm # Модель базы данных для таблицы rooms
    schema = Facility  # Схема данных для сериализации комнат
