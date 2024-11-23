from datetime import date

from sqlalchemy import select, func

from src.models.bookings import BookingOrm  # Модель, представляющая таблицу с бронями (bookings)
from src.models.rooms import RoomsORM  # Модель, представляющая таблицу с комнатами (rooms)
from src.repositories.base import BaseRepository  # Базовый репозиторий, обеспечивающий базовые операции с БД
from src.schemas.rooms import Room  # Pydantic-схема для комнат


# Репозиторий для работы с комнатами (rooms)
class RoomsRepository(BaseRepository):
    # Связываем ORM-модель и Pydantic-схему с репозиторием
    model = RoomsORM  # Модель базы данных для таблицы rooms
    schema = Room  # Схема данных для сериализации комнат

    # Асинхронный метод для получения свободных комнат в заданный период времени
    async def get_filtered_by_time(
            self,
            hotel_id,  # ID отеля, для которого ищем комнаты
            date_from: date,  # Дата начала периода
            date_to: date,  # Дата окончания периода
    ):
        # Подзапрос для подсчета количества занятых комнат по ID комнаты
        rooms_count = (
            select(BookingOrm.room_id,
                   func.count("*").label("rooms_booked"))  # Выбираем ID комнаты и количество бронирований
            .select_from(BookingOrm)  # Указываем таблицу bookings как источник
            .filter(
                BookingOrm.date_from <= date_to,  # Фильтр: дата начала бронирования не позже конца заданного периода
                BookingOrm.date_to >= date_from
                # Фильтр: дата окончания бронирования не раньше начала заданного периода
            )
            .group_by(BookingOrm.room_id)  # Группируем по ID комнаты
            .cte(name="rooms_count")  # Создаем CTE (общую табличную экспрессию) с названием "rooms_count"
        )

        # Подзапрос для расчета оставшихся свободных комнат по каждой комнате
        rooms_left_table = (
            select(
                RoomsORM.id.label("room_id"),  # Выбираем ID комнаты
                (RoomsORM.quantity - func.coalesce(rooms_count.c.rooms_booked, 0)).label("rooms_left"),
                # Количество свободных комнат
            )
            .select_from(RoomsORM)  # Указываем таблицу rooms как источник
            .outerjoin(rooms_count, RoomsORM.id == rooms_count.c.room_id)  # Левое соединение с CTE rooms_count
            .cte(name="rooms_left_table")  # Создаем CTE с названием "rooms_left_table"
        )

        # Подзапрос для получения всех ID комнат в указанном отеле
        rooms_ids_for_hotels = (
            select(RoomsORM.id)  # Выбираем ID комнат
            .select_from(RoomsORM)  # Указываем таблицу rooms как источник
            .filter_by(hotel_id=hotel_id)  # Фильтруем по ID отеля
            .subquery(name="rooms_ids_for_hotel")  # Преобразуем в подзапрос с именем "rooms_ids_for_hotel"
        )

        # Финальный подзапрос для получения ID комнат, которые свободны в заданный период времени
        rooms_ids_to_get = (
            select(rooms_left_table.c.room_id)  # Выбираем только ID комнат
            .select_from(rooms_left_table)  # Указываем CTE rooms_left_table как источник
            .filter(
                rooms_left_table.c.rooms_left > 0,  # Комнаты должны быть свободны (количество оставшихся больше 0)
                rooms_left_table.c.room_id.in_(rooms_ids_for_hotels.select()),
                # Комнаты должны принадлежать указанному отелю
            )
        )

        # Используем базовый метод get_filtered для фильтрации комнат
        # Здесь `RoomsORM.id.in_(rooms_ids_to_get)` добавляет условие на ID комнат
        return await self.get_filtered(RoomsORM.id.in_(rooms_ids_to_get))
