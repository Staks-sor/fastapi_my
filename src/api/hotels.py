from datetime import date

from fastapi import Query, APIRouter, Body, HTTPException

from src.api.dependencies import PaginationDep, DBDep
from src.database import async_session_maker
from src.repositories.hotels import HotelsRepository
from src.schemas.hotels import Hotel, HotelPATCH, HotelAdd

router = APIRouter(prefix="/hotels", tags=['Отели'])


@router.get("",
            summary="Получение данных об отелях",
            description="<h1>Тут мы получаем данные об отелях</h1>", )
async def get_hotels(
        pagination: PaginationDep,
        db: DBDep,
        location: str | None = Query(None, description="Адрес отеля"),
        title: str | None = Query(None, description="Название отеля"),
        date_from: date = Query(example="2024-08-01"),
        date_to: date = Query(example="2024-08-01"),

):
    per_page = pagination.per_page or 5
    return await db.hotels.get_filtered_by_time(
        date_from=date_from,
        date_to=date_to,
        location=location,
        title=title,
        limit=per_page,
        offset=per_page * (pagination.page - 1)
    )


@router.get("/{hotel_id}",
            summary="Получение одного отеля",
            description="<h1>Тут мы получаем один отель</h1>", )
async def get_hotels(hotel_id: int, db: DBDep):
    return await db.hotels.get_one_or_none(id=hotel_id)


@router.post("",
             summary="Добавление отеля",
             description="<h1>Тут мы добовляем отель</h1>", )
async def create_hotel(
        db: DBDep,
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
    new_hotel = await db.hotels.add(hotel_data)
    await db.session.commit()
    return {"status": "OK", "data": new_hotel}


@router.put("/{hotel_id}",
            summary="Полное обновление данных об отеле",
            description="<h1>Тут мы обновляем данные полностью</h1>", )
async def put_change_all(
        db: DBDep,
        hotel_id: int,
        hotel_data: Hotel = Body(),
):
    await db.hotels.edit(hotel_data, id=hotel_id)
    await db.session.commit()
    return {"status": "OK"}


# PATCH: Частичное обновление информации об отеле
@router.patch(
    "/{hotel_id}",
    summary="Частичное обновление данных об отеле",
    description="<h1>Тут мы частично обновляем данные об отеле: можно менять один из параметров</h1>",
)
async def patch_change_uniq(
        db: DBDep,
        hotel_id: int,
        hotel_data: HotelPATCH

):
    async with async_session_maker() as session:
        # Создаем репозиторий и передаем сессию
        await db.hotels.edit(hotel_data, exclude_unset=True, id=hotel_id)
        await db.session.commit()
        # Возвращаем статус OK и обновленные данные
        return {"status": "OK"}


@router.delete("/{hotel_id}",
               summary="Удаление отеля",
               description="<h1>Тут мы удаляем отель</h1>", )
async def delete_hotels(db: DBDep, hotel_id: int):
    await db.hotels.delete(id=hotel_id)
    await db.session.commit()
    return {"status": "ok"}
