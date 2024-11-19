from datetime import date

from fastapi import Query, APIRouter, Body

from src.api.dependencies import DBDep
from src.database import async_session_maker
from src.repositories.rooms import RoomsRepository
from src.schemas.rooms import RoomAdd, RoomAddRequest, RoomPatchRequest, RoomPatch

router = APIRouter(prefix="/hotels", tags=["Номера"])


@router.get("/{hotel_id}/rooms",
            summary="Получение данных о комнатах",
            description="<h1>Тут мы получаем данные о комнатах</h1>", )
async def get_rooms(
        db: DBDep,
        hotel_id: int,
        date_from: date = Query(example="2024-08-01"),
        date_to: date = Query(example="2024-08-01")

):
    return await db.rooms.get_filtered_by_time(hotel_id=hotel_id, date_from=date_from, date_to=date_to)


@router.get("/{hotel_id}/rooms/{room_id}",
            summary="Получение одного отеля",
            description="<h1>Тут мы получаем один отель</h1>", )
async def get_hotels(db: DBDep, hotel_id: int, room_id: int):
    return await db.rooms.get_one_or_none(id=room_id, hotel_id=hotel_id)


@router.post("/{hotel_id}/rooms",
             summary="Добавление Комнаты",
             description="<h1>Тут мы добавляем комнату</h1>", )
async def create_room(hotel_id: int, room_data: RoomAddRequest = Body()):
    async with async_session_maker() as session:
        _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
        new_room = await RoomsRepository(session).add(_room_data)
        await session.commit()
    return {"status": "OK", "data": new_room}


@router.put("/{hotel_id}/rooms/{room_id}",
            summary="Полное обновление данных о комнатах",
            description="<h1>Тут мы обновляем данные полностью</h1>", )
async def edit_room(
        hotel_id: int,
        room_id: int,
        room_data: RoomAddRequest,
):
    _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump(), exclude_unset=True)
    async with async_session_maker() as session:
        # Создаем репозиторий и передаем сессию
        await RoomsRepository(session).edit(_room_data, exlude_unset=True, id=room_id)
        await session.commit()
        # Возвращаем статус OK и обновленные данные
        return {"status": "OK"}


# PATCH: Частичное обновление информации об отеле
@router.patch(
    "/{hotel_id}/rooms/{room_id}",
    summary="Частичное обновление данных об отеле",
    description="<h1>Тут мы частично обновляем данные об отеле: можно менять один из параметров</h1>",
)
async def partially_edit_room(
        hotel_id: int,
        room_id: int,
        room_data: RoomPatchRequest,

):
    _room_data = RoomPatch(hotel_id=hotel_id, **room_data.model_dump(exclude_unset=True))
    async with async_session_maker() as session:
        # Создаем репозиторий и передаем сессию
        await RoomsRepository(session).edit(_room_data, exclude_unset=True, id=room_id, hotel_id=hotel_id)
        await session.commit()
        # Возвращаем статус OK и обновленные данные
        return {"status": "OK"}


@router.delete("/{hotel_id}/rooms{room_id}",
               summary="Удаление отеля",
               description="<h1>Тут мы удаляем отель</h1>", )
async def delete_hotels(hotel_id: int, room_id: int):
    async with async_session_maker() as session:
        await RoomsRepository(session).delete(id=room_id, hotel_id=hotel_id)
        await session.commit()

    return {"status": "ok"}
