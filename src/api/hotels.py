from fastapi import Query, HTTPException, APIRouter, Body

from sqlalchemy import insert

from src.api.dependencies import PaginationDep
from src.database import async_session_maker, engine
from src.models.hotels import HotelsORM
from src.schemas.hotels import Hotel, HotelPATCH

router = APIRouter(prefix="/hotels", tags=['Отели'])


# Задание №1
# Put: Полное изменение
@router.put("/{hotel_id}",
            summary="Полное обновление данных об отеле",
            description="<h1>Тут мы обновляем данные полностью</h1>", )
def put_change_all(
        hotel_id: int,
        hotel_data: Hotel,
):
    global hotels
    for hotel in hotels:
        if hotel["id"] == hotel_id:
            hotel["title"] = hotel_data.title
            hotel["name"] = hotel_data.name
            return {"status": "ok", "updated_hotel": hotel}

    # Если отель с таким id не найден
    raise HTTPException(status_code=404, detail="Hotel not found")


# PATCH: Частичное обновление информации об отеле
@router.patch(
    "/{hotel_id}",
    summary="Частичное обновление данных об отеле",
    description="<h1>Тут мы частично обновляем данные об отеле: можно менять один из параметров</h1>",
)
def patch_change_uniq(
        hotel_id: int,
        hotel_data: HotelPATCH

):
    global hotels
    for hotel in hotels:
        if hotel["id"] == hotel_id:
            # Обновляем только если значение не None и не равно "string"
            if hotel_data.title is not None and hotel_data.title != "string":
                hotel["title"] = hotel_data.title
            if hotel_data.name is not None and hotel_data.name != "string":
                hotel["name"] = hotel_data.name

            return {"status": "ok", "updated_hotel": hotel}

    # Если отель с таким id не найден
    raise HTTPException(status_code=404, detail="Hotel not found")


# Конец первого задания.


@router.post("",
             summary="Добавление отеля",
             description="<h1>Тут мы добовляем отель</h1>", )
async def create_hotel(
        hotel_data: Hotel = Body(openapi_examples={
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
        add_hotel_stmt = insert(HotelsORM).values(**hotel_data.model_dump())
        # Как сделать просмотр запроса с целью дебага или понимания какой запрос улетел от алхимии
        # print(add_hotel_stmt.compile(engine, compile_kwargs={"literal_binds": True}))
        await session.execute(add_hotel_stmt)
        await session.commit()

    return {"status": "ok"}


@router.delete("/{hotel_id}",
               summary="Удаление отеля",
               description="<h1>Тут мы удаляем отель</h1>", )
def delete_hotels(hotel_id: int):
    global hotels
    hotels = [hotel for hotel in hotels if hotel["id"] != hotel_id]

    return {"status": "ok"}


@router.get("",
            summary="Получение данных об отелях",
            description="<h1>Тут мы получаем данные об отелях</h1>", )
def get_hotels(
        pagination: PaginationDep,
        id: int | None = Query(None, description="Айди отеля"),
        title: str | None = Query(None, description="Название отеля"),

):
    hotels_ = []
    for hotel in hotels:
        if id and hotel["id"] != id:
            continue
        if title and hotel["title"] != title:
            continue
        hotels_.append(hotel)
    if pagination.page and pagination.per_page:
        return hotels_[pagination.per_page * (pagination.page - 1):][:pagination.per_page]

    return hotels_
