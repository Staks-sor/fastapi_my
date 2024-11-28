from datetime import date

from fastapi import Query, APIRouter, Body

from src.api.dependencies import DBDep
from src.database import async_session_maker
from src.repositories.rooms import RoomsRepository
from src.schemas.facilities import FacilityAdd
from src.schemas.rooms import RoomAdd, RoomAddRequest, RoomPatchRequest, RoomPatch

router = APIRouter(prefix="/facilities", tags=["Удобства"])


@router.get("",
            summary="Получение данных о комфорте в комнатах",
            description="<h1>Тут мы получаем данные о комфорте в комнатах</h1>", )
async def get_facilities(db: DBDep, ):
    return await db.facilities.get_all()


@router.post("")
async def create_facilities(db: DBDep, facility_data: FacilityAdd = Body()):
    facility = await db.facilities.add(facility_data)
    await db.commit()

    return {"status": "OK", "data": facility}