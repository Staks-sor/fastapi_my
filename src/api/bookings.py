from fastapi import APIRouter

from src.api.dependencies import DBDep, UserIdDep
from src.schemas.bookings import BookingAddRequest, BookingAdd

router = APIRouter(prefix="/bookings", tags=['Бронирование'])


@router.get("")
async def get_booking(db: DBDep):
    return await db.bookings.get_all()


@router.get("/me")
async def get_booking(user_id: UserIdDep, db: DBDep):
    return await db.bookings.get_filtered(user_id=user_id)


@router.post("")
async def add_booking(user_id: UserIdDep,
                      db: DBDep,
                      booking_data: BookingAddRequest,
                      ):
    room = await db.rooms.get_one_or_none(id=booking_data.room_id)
    room_price: int = room.price
    booking_data = BookingAdd(
        user_id=user_id,
        price=room_price,
        **booking_data.model_dump()
    )
    booking = await db.bookings.add(booking_data)
    await db.commit()
    return {"status": "Ok", "data": booking}
