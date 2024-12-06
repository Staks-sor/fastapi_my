from sqlalchemy import select, delete, insert
from src.models.facilities import FacilitiesOrm, RoomsFacilitiesOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import FacilityDataMapper
from src.schemas.facilities import Facility, RoomsFacility


# Репозиторий для работы с таблицей "facilities" (удобства)
class FacilitiesRepository(BaseRepository):
    """
    Репозиторий для работы с удобствами.

    Attributes:
        model: ORM-модель, связанная с таблицей "facilities".
        schema: Pydantic-схема для сериализации данных об удобствах.
    """
    model = FacilitiesOrm
    mapper = FacilityDataMapper


# Репозиторий для работы с таблицей связей "rooms_facilities"
class RoomsFacilitiesRepository(BaseRepository):
    """
    Репозиторий для работы с Many-to-Many связями между комнатами и удобствами.

    Attributes:
        model: ORM-модель, связанная с таблицей "rooms_facilities".
        schema: Pydantic-схема для сериализации данных о связях.
    """
    model = RoomsFacilitiesOrm
    schema = RoomsFacility

    async def set_room_facilities(self, room_id: int, facilities_ids: list[int]) -> None:
        """
        Устанавливает список удобств для указанной комнаты.
        Удаляет неудобства, которые больше не актуальны, и добавляет новые.

        Args:
            room_id (int): ID комнаты, для которой нужно установить удобства.
            facilities_ids (list[int]): Список ID удобств, которые нужно связать с комнатой.

        Returns:
            None
        """
        # Получаем текущий список ID удобств, связанных с данной комнатой
        get_current_facilities_ids_query = (
            select(self.model.facility_id)
            .filter_by(room_id=room_id)
        )
        result = await self.session.execute(get_current_facilities_ids_query)
        current_facilities_ids: list[int] = result.scalars().all()

        # Определяем, какие связи нужно удалить, а какие добавить
        ids_to_delete: list[int] = list(set(current_facilities_ids) - set(facilities_ids))
        ids_to_insert: list[int] = list(set(facilities_ids) - set(current_facilities_ids))

        # Удаляем устаревшие связи
        if ids_to_delete:
            delete_m2m_facilities_stmt = (
                delete(self.model)
                .filter(
                    self.model.room_id == room_id,
                    self.model.facility_id.in_(ids_to_delete),
                )
            )
            await self.session.execute(delete_m2m_facilities_stmt)

        # Добавляем новые связи
        if ids_to_insert:
            insert_m2m_facilities_stmt = (
                insert(self.model)
                .values([{"room_id": room_id, "facility_id": f_id} for f_id in ids_to_insert])
            )
            await self.session.execute(insert_m2m_facilities_stmt)
