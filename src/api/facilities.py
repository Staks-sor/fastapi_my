from datetime import date

from fastapi import Query, APIRouter, Body

from src.api.dependencies import DBDep
from src.database import async_session_maker
from src.repositories.rooms import RoomsRepository
from src.schemas.rooms import RoomAdd, RoomAddRequest, RoomPatchRequest, RoomPatch

router = APIRouter(prefix="/facilities", tags=["комфорт"])


@router.get("/{facilities_id}/rooms",
            summary="Получение данных о комфорте в комнатах",
            description="<h1>Тут мы получаем данные о комфорте в комнатах</h1>", )
async def get_facilities(
        db: DBDep,
        facilities_id: int,

):
    return await db.facilities.get_filtered_by_time(facilities_id=facilities_id, )
