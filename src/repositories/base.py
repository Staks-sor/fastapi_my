from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import select, insert, update, delete
from sqlalchemy.orm import joinedload

from src.models.rooms import RoomsORM
from src.schemas.rooms import RoomWithRels


class BaseRepository:
    model = None
    schema: BaseModel = None

    def __init__(self, session):
        self.session = session

    async def get_filtered(self, *filter, **filter_by):
        query = (
            select(self.model)
            .filter(*filter)
            .filter_by(**filter_by)
        )
        result = await self.session.execute(query)
        return [self.schema.model_validate(model) for model in result.scalars().all()]

    async def get_all(self, *args, **kwargs):
        return await self.get_filtered()

    async def get_one_or_none(self, **filter_by):
        query = (
            select(self.model)
            .options(joinedload(self.model.facilities))  # Для загрузки связанных данных
            .filter_by(**filter_by)
        )
        result = await self.session.execute(query)

        # Применяем unique() перед scalars()
        model = result.unique().scalars().one_or_none()

        if model is None:
            return None

        # Возвращаем результат с применением модели
        return RoomWithRels.model_validate(model)

    async def add(self, data: BaseModel):
        add_data_stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        result = await self.session.execute(add_data_stmt)
        model = result.scalars().one()
        return self.schema.model_validate(model)

    async def add_bulk(self, data: list[BaseModel]):
        add_data_stmt = insert(self.model).values([item.model_dump() for item in data])
        await self.session.execute(add_data_stmt)

    async def edit(self, data: BaseModel, exclude_unset: bool = False, **filter_by) -> None:
        update_stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=exclude_unset))  # Передаем данные для обновления
        )
        result = await self.session.execute(update_stmt)

        if result.rowcount == 0:
            raise HTTPException(status_code=402, detail="Такого ID нет.")

        await self.session.execute(update_stmt)

    async def delete(self, **filter_by):
        delete_stmt = delete(self.model).filter_by(**filter_by)
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        hotel = result.scalars().one_or_none()

        # Если объект не найден, выбрасываем исключение 404
        if hotel is None:
            raise HTTPException(status_code=404, detail="Hotel not found")
        await self.session.execute(delete_stmt)
        return delete_stmt
