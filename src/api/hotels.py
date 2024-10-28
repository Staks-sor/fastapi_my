from fastapi import Query, APIRouter, Body

from src.api.dependencies import PaginationDep
from src.database import async_session_maker
from src.repositories.hotels import HotelsRepository
from src.schemas.hotels import Hotel, HotelPATCH, HotelAdd

router = APIRouter(prefix="/hotels", tags=['Отели'])


@router.put("/{hotel_id}",
            summary="Полное обновление данных об отеле",
            description="<h1>Тут мы обновляем данные полностью</h1>", )
async def put_change_all(
        hotel_id: int,
        hotel_data: Hotel = Body(),
):
    async with async_session_maker() as session:
        # Создаем репозиторий и передаем сессию
        await HotelsRepository(session).edit(hotel_data, id=hotel_id)
        await session.commit()
        # Возвращаем статус OK и обновленные данные
        return {"status": "OK"}


# PATCH: Частичное обновление информации об отеле
@router.patch(
    "/{hotel_id}",
    summary="Частичное обновление данных об отеле",
    description="<h1>Тут мы частично обновляем данные об отеле: можно менять один из параметров</h1>",
)
async def patch_change_uniq(
        hotel_id: int,
        hotel_data: HotelPATCH

):
    async with async_session_maker() as session:
        # Создаем репозиторий и передаем сессию
        await HotelsRepository(session).edit(hotel_data, exclude_unset=True, id=hotel_id)
        await session.commit()
        # Возвращаем статус OK и обновленные данные
        return {"status": "OK"}


@router.post("",
             summary="Добавление отеля",
             description="<h1>Тут мы добовляем отель</h1>", )
async def create_hotel(
        hotel_data: HotelAdd = Body(openapi_examples={
            "1": {"summary": "Сочи", "value": {
                "title": "Отель Сочи 5 звезд у моря",
                "location": "ул. Моря, 1",
            }},
            "2": {"summary": "Дубай", "value": {
                "title": "Отель Дубаи у фонтана",
                "location": "ул. Шейха, 2",
            }},
        })
):
    async with async_session_maker() as session:
        new_hotel = await HotelsRepository(session).add(hotel_data)
        await session.commit()
    return {"status": "OK", "data": new_hotel}


@router.delete("/{hotel_id}",
               summary="Удаление отеля",
               description="<h1>Тут мы удаляем отель</h1>", )
async def delete_hotels(hotel_id: int):
    async with async_session_maker() as session:
        await HotelsRepository(session).delete(id=hotel_id)
        await session.commit()

    return {"status": "ok"}


@router.get("",
            summary="Получение данных об отелях",
            description="<h1>Тут мы получаем данные об отелях</h1>", )
async def get_hotels(
        pagination: PaginationDep,
        location: str | None = Query(None, description="Адрес отеля"),
        title: str | None = Query(None, description="Название отеля"),

):
    per_page = pagination.per_page or 5
    async with async_session_maker() as session:
        return await HotelsRepository(session).get_all(
            location=location,
            title=title,
            limit=per_page,
            offset=per_page * (pagination.page - 1)
        )


@router.get("/{hotel_id}",
            summary="Получение одного отеля",
            description="<h1>Тут мы получаем один отель</h1>", )
async def get_hotels(hotel_id: int):
    async with async_session_maker() as session:
        return await HotelsRepository(session).get_one_or_none(id=hotel_id)
