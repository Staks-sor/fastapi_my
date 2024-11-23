from fastapi import APIRouter, HTTPException

from src.api.dependencies import DBDep, UserIdDep  # Зависимости для базы данных и идентификатора пользователя
from src.schemas.bookings import BookingAddRequest, BookingAdd  # Pydantic-схемы для работы с запросами на бронирование

# Создаем маршрутизатор для работы с бронированиями
router = APIRouter(prefix="/bookings", tags=['Бронирование'])


# Эндпоинт для получения всех бронирований
@router.get("")
async def get_booking(db: DBDep):  # Используем зависимость для базы данных
    """
    Возвращает список всех бронирований.
    """
    return await db.bookings.get_all()  # Вызываем метод репозитория для получения всех записей бронирований


# Эндпоинт для получения бронирований текущего пользователя
@router.get("/me")
async def get_booking(user_id: UserIdDep, db: DBDep):
    """
    Возвращает список бронирований, связанных с текущим пользователем.
    """
    return await db.bookings.get_filtered(user_id=user_id)  # Фильтруем бронирования по user_id


# Эндпоинт для создания нового бронирования
@router.post("")
async def add_booking(
        user_id: UserIdDep,  # ID текущего пользователя, извлекается через токен
        db: DBDep,  # Объект для работы с базой данных
        booking_data: BookingAddRequest,  # Входные данные для бронирования, валидируемые через Pydantic-схему
):
    """
    Создает новое бронирование для пользователя.
    """
    # Получаем информацию о комнате по ее ID
    room = await db.rooms.get_one_or_none(id=booking_data.room_id)

    # Проверяем, существует ли указанная комната
    if not room:
        raise HTTPException(status_code=404, detail="Комната не найдена")

    # Получаем цену комнаты
    room_price: int = room.price

    # Создаем объект бронирования, включая user_id, цену комнаты и данные из запроса
    booking_data = BookingAdd(
        user_id=user_id,  # ID пользователя, создавшего бронирование
        price=room_price,  # Цена за бронирование
        **booking_data.model_dump()  # Распаковываем данные из схемы BookingAddRequest
    )

    # Добавляем бронирование в базу данных через репозиторий
    booking = await db.bookings.add(booking_data)

    # Сохраняем изменения в базе данных
    await db.commit()

    # Возвращаем успешный ответ с данными о созданном бронировании
    return {"status": "Ok", "data": booking}

