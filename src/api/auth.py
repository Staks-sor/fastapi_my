from fastapi import APIRouter, HTTPException, Response

from src.api.dependencies import UserIdDep  # Зависимость для получения идентификатора пользователя из токена
from src.database import async_session_maker  # Асинхронный фабричный метод для создания сессии базы данных
from src.repositories.users import UsersRepository  # Репозиторий для работы с таблицей пользователей
from src.schemas.users import UserRequestAdd, UserAdd  # Pydantic-схемы для запросов и добавления пользователей
from src.services.auth import AuthService  # Сервис для работы с аутентификацией (хеширование паролей, токены)

# Создаем маршрутизатор для авторизации и аутентификации пользователей
router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])


# Эндпоинт для регистрации нового пользователя
@router.post("/register")
async def register_user(
        data: UserRequestAdd,  # Данные запроса (email и пароль), валидируемые через Pydantic-схему
):
    # Хешируем пароль, чтобы его безопасно хранить в базе данных
    hashed_password = AuthService().hash_password(data.password)

    # Создаем объект для нового пользователя
    new_user_data = UserAdd(email=data.email, hashed_password=hashed_password)

    # Открываем асинхронную сессию с базой данных
    async with async_session_maker() as session:
        # Добавляем нового пользователя в базу данных через репозиторий
        await UsersRepository(session).add(new_user_data)
        # Фиксируем изменения в базе данных
        await session.commit()

    # Возвращаем успешный ответ
    return {"status": "ok"}


# Эндпоинт для авторизации пользователя (логин)
@router.post("/login")
async def login_user(
        data: UserRequestAdd,  # Данные запроса (email и пароль)
        response: Response,  # Объект для управления HTTP-ответом (например, установка cookies)
):
    # Открываем асинхронную сессию с базой данных
    async with async_session_maker() as session:
        # Получаем пользователя и его хешированный пароль из базы данных
        user = await UsersRepository(session).get_user_with_hashed_password(email=data.email)
        # Если пользователь не найден, возвращаем ошибку авторизации
        if not user:
            raise HTTPException(status_code=401, detail="Авторизация не выполнена")
        # Проверяем соответствие пароля, используя сервис AuthService
        if not AuthService().verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Пароль не верный")
        # Генерируем JWT-токен для авторизованного пользователя
        access_token = AuthService().create_access_token({"user_id": user.id})
        # Устанавливаем токен в cookies ответа
        response.set_cookie("access_token", access_token)
        # Возвращаем токен в теле ответа
        return {"access_token": access_token}


# Эндпоинт для получения информации о текущем пользователе
@router.get(
    "/me",
    summary="Получение куки пользователя",  # Краткое описание эндпоинта для Swagger документации
    description="<h1>Тут мы получаем инфу о пользователе</h1>",  # Детальное описание для Swagger
)
async def get_me(user_id: UserIdDep, ):  # ID пользователя извлекается из токена через зависимость UserIdDep
    # Открываем асинхронную сессию с базой данных
    async with async_session_maker() as session:
        # Получаем информацию о пользователе по ID
        user = await UsersRepository(session).get_one_or_none(id=user_id)
        # Возвращаем данные о пользователе
        return user


# Эндпоинт для выхода пользователя (logout)
@router.post("/logout")
async def logout(response: Response):
    # Удаляем токен из cookies
    response.delete_cookie(key="access_token")
    # Возвращаем сообщение об успешном выходе
    return {"message": "Logged out successfully"}
