from fastapi import Query, HTTPException, APIRouter, Body

from sqlalchemy import insert, select, func

from src.api.dependencies import PaginationDep
from src.database import async_session_maker, engine
from src.models.hotels import HotelsORM
from src.repositories.hotels import HotelsRepository
from src.schemas.hotels import Hotel, HotelPATCH

router = APIRouter(prefix="/hotels", tags=['Отели'])


# Задание №1
# Put: Полное изменение
@router.put("/{hotel_id}",
            summary="Полное обновление данных об отеле",
            description="<h1>Тут мы обновляем данные полностью</h1>", )
async def put_change_all(
        hotel_id: int,
        hotel_data: Hotel = Body(),
):
    async with async_session_maker() as session:
        # Создаем репозиторий и передаем сессию
        hotels_repo = HotelsRepository(session)

        # Пробуем изменить отель с данным ID
        try:
            change_hotel = await hotels_repo.edit(hotel_data, id=hotel_id)
            await session.commit()
        except HTTPException as e:
            raise e  # Перехватываем ошибку и возвращаем 404 если отель не найден

        # Возвращаем статус OK и обновленные данные
        return {"status": "OK", "data": change_hotel}


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

# Задание № 5
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
        new_hotel = await HotelsRepository(session).add(hotel_data)
        await session.commit()
    return {"status": "OK", "data": new_hotel}
    # return .compile(engine, compile_kwargs={"literal_binds": True})


# Конец 5 задания
@router.delete("/{hotel_id}",
               summary="Удаление отеля",
               description="<h1>Тут мы удаляем отель</h1>", )
async def delete_hotels(hotel_id: int):
    async with async_session_maker() as session:
        await HotelsRepository(session).delete(id=hotel_id)
        await session.commit()

    return {"status": "ok"}


# Задание № 4 Фильтрация по подстроке
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
