from datetime import date

from sqlalchemy import select, func

from src.models.bookings import BookingOrm
from src.models.rooms import RoomsORM


async def rooms_ids_for_booking(
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
            RoomsORM.id.label("room_id"),
            (RoomsORM.quantity - func.coalesce(rooms_count.c.rooms_booked, 0)).label("rooms_left"),
        )
        .select_from(RoomsORM)
        .outerjoin(rooms_count, RoomsORM.id == rooms_count.c.room_id)
        .cte(name="rooms_left_table")
    )

    rooms_ids_for_hotels = (
        select(RoomsORM.id)
        .select_from(RoomsORM)
        .filter_by(hotel_id=hotel_id)
        .subquery(name="rooms_ids_for_hotel")
    )

    rooms_ids_to_get = (
        select(rooms_left_table.c.room_id)
        .select_from(rooms_left_table)
        .filter(rooms_left_table.c.rooms_left > 0,
                rooms_left_table.c.room_id.in_(rooms_ids_for_hotels.select()),
                )
    )

    # print(rooms_ids_to_get.compile(bind=engine, compile_kwargs={"literal_binds": True}))
    # print(str(rooms_ids_to_get))

    return await self.get_filtered(RoomsORM.id.in_(rooms_ids_to_get))
