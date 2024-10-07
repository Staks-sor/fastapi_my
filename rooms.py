from fastapi import Query, HTTPException, APIRouter

router = APIRouter(prefix="/rooms", tags=['Комнаты'])


@router.get("",
            summary="Получение данных об отелях",
            description="<h1>Тут мы получаем данные об отелях</h1>", )
def get_rooms(
        id: int | None = Query(None, description="Айди отеля"),
        title: str | None = Query(None, description="Название отеля"),
):
    ...
