from fastapi import APIRouter, Body, Query
from src.database import async_session_maker
from src.repositories.rooms import RoomsRepository
from src.schemas.rooms import Room, RoomAdd
from src.api.dependencies import PaginationDep

router = APIRouter(prefix="/rooms", tags=["Комнаты"])


# PUT: Полное обновление данных о комнате
@router.put("/{room_id}",
            summary="Полное обновление данных о комнате",
            description="<h1>Тут мы обновляем данные о комнате полностью</h1>")
async def put_update_room(
        room_id: int,
        room_data: Room = Body()
):
    async with async_session_maker() as session:
        await RoomsRepository(session).edit(room_data, id=room_id)
        await session.commit()
        return {"status": "OK"}


# PATCH: Частичное обновление данных о комнате
# @router.patch("/{room_id}",
#               summary="Частичное обновление данных о комнате",
#               description="<h1>Тут мы частично обновляем данные о комнате: можно менять один из параметров</h1>")
# async def patch_update_room(
#         room_id: int,
#         room_data: RoomPATCH
# ):
#     async with async_session_maker() as session:
#         await RoomsRepository(session).edit(room_data, exclude_unset=True, id=room_id)
#         await session.commit()
#         return {"status": "OK"}


# POST: Добавление новой комнаты
@router.post("",
             summary="Добавление комнаты",
             description="<h1>Тут мы добавляем комнату в отель</h1>")
async def create_room(
        hotel_id: int,
        room_data: RoomAdd = Body(...)
):
    async with async_session_maker() as session:
        new_room = await RoomsRepository(session).add(room_data, hotel_id=hotel_id)
        await session.commit()
    return {"status": "OK", "data": new_room}


# DELETE: Удаление комнаты
@router.delete("/{room_id}",
               summary="Удаление комнаты",
               description="<h1>Тут мы удаляем комнату</h1>")
async def delete_room(room_id: int):
    async with async_session_maker() as session:
        await RoomsRepository(session).delete(id=room_id)
        await session.commit()
    return {"status": "ok"}


# GET: Получение всех комнат для заданного отеля
@router.get("",
            summary="Получение данных о комнатах",
            description="<h1>Тут мы получаем данные о комнатах для отеля</h1>")
async def get_rooms(
        hotel_id: int,
        pagination: PaginationDep,
        title: str | None = Query(None, description="Название комнаты"),
):
    per_page = pagination.per_page or 5
    async with async_session_maker() as session:
        return await RoomsRepository(session).get_all(
            hotel_id=hotel_id,
            title=title,
            limit=per_page,
            offset=per_page * (pagination.page - 1)
        )


# GET: Получение информации о конкретной комнате
@router.get("/{room_id}",
            summary="Получение одной комнаты",
            description="<h1>Тут мы получаем информацию о конкретной комнате</h1>")
async def get_room(room_id: int):
    async with async_session_maker() as session:
        return await RoomsRepository(session).get_one_or_none(id=room_id)
