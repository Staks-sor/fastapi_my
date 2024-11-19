from datetime import date

from sqlalchemy import select, func

from src.database import engine
from src.models.bookings import BookingOrm
from src.models.rooms import RoomsORM
from src.repositories.base import BaseRepository
from src.schemas.rooms import Room


class RoomsRepository(BaseRepository):
    model = RoomsORM
    schema = Room

    async def get_filtered_by_time(
            self,
            hotel_id,
            date_from: date,
            date_to: date,
    ):
        rooms_count = (
            select(BookingOrm.room_id, func.count("*").label("rooms_booked"))
            .select_from(BookingOrm)
            .filter(
                BookingOrm.date_from <= date_to,
                BookingOrm.date_to >= date_from
            )
            .group_by(BookingOrm.room_id)
            .cte(name="rooms_count")
        )

        rooms_left_table = (
            select(
                RoomsORM.id.label("room-id"),
                (RoomsORM.quantity - func.coalesce(rooms_count.c.rooms_booked, 0)).label("rooms_left"),
            )
            .select_from(RoomsORM)
            .outerjoin(rooms_count, RoomsORM.id == rooms_count.c.room_id)
            .cte(name="rooms_left_table")
        )

        query = (
            select(rooms_left_table)
            .select_from(rooms_left_table)
            .filter(rooms_left_table.c.rooms_left > 0)
        )

        print(query.compile(bind=engine, compile_kwargs={"literal_binds": True}))
