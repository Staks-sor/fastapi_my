from sqlalchemy import select, delete, insert

from src.models.facilities import FacilitiesOrm, \
    RoomsFacilitiesOrm  # Модель, представляющая таблицу с комнатами (rooms)
from src.repositories.base import BaseRepository  # Базовый репозиторий, обеспечивающий базовые операции с БД
from src.schemas.facilities import Facility, RoomsFacility  # Pydantic-схема для комнат


# Репозиторий для работы с комнатами (rooms)
class FacilitiesRepository(BaseRepository):
    # Связываем ORM-модель и Pydantic-схему с репозиторием
    model = FacilitiesOrm  # Модель базы данных для таблицы rooms
    schema = Facility  # Схема данных для сериализации комнат


class RoomsFacilitiesRepository(BaseRepository):
    model = RoomsFacilitiesOrm
    schema = RoomsFacility

    async def set_room_facilities(self, room_id: int, facilities_ids: list[int]):
        get_current_facilities_ids_query = (
            select(self.model.facility_id)
            .filter_by(room_id=room_id)
        )
        result = await self.session.execute(get_current_facilities_ids_query)
        current_facilities_ids: list[int] = result.scalars().all()
        ids_to_delete: list[int] = list(set(current_facilities_ids) - set(facilities_ids))
        ids_to_insert: list[int] = list(set(facilities_ids) - set(current_facilities_ids))

        if ids_to_delete:
            delete_m2m_facilities_stmt = (
                delete(self.model)
                .filter(
                    self.model.room_id == room_id,
                    self.model.facility_id.in_(ids_to_delete),
                )
            )
            await self.session.execute(delete_m2m_facilities_stmt)

        if ids_to_insert:
            insert_m2m_facilities_stmt = (
                insert(self.model)
                .values([{"room_id": room_id, "facility_id": f_id} for f_id in ids_to_insert])
            )
            await self.session.execute(insert_m2m_facilities_stmt)

