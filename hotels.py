from fastapi import Query, HTTPException, APIRouter

from schemas.hotels import Hotel, HotelPATCH

router = APIRouter(prefix="/hotels", tags=['Отели'])

hotels = [
    {"id": 1, "title": "Sochi", "name": "sochi"},
    {"id": 2, "title": "Dubai", "name": "dubai"},
]


# Проверка работы для понимания асинхронных и синхронных функций


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
def create_hotel(
        hotel_data: Hotel
):
    global hotels
    hotels.append({
        "id": hotels[-1]["id"] + 1,
        "title": hotel_data.title,
        "name": hotel_data.name,
    })
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
    return hotels_
