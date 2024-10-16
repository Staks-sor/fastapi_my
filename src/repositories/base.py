from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import select, insert, update, delete

from src.schemas.hotels import Hotel


class BaseRepository:
    model = None
    schema: BaseModel = None

    def __init__(self, session):
        self.session = session

    async def get_all(self, *args, **kwargs):
        query = select(self.model)
        result = await self.session.execute(query)
        return [self.schema.model_validate(model) for model in result.scalars().all()]

    async def get_one_or_none(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        if model is None:
            return None
        return self.schema.model_validate(model)

    async def add(self, data: BaseModel):
        add_data_stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        result = await self.session.execute(add_data_stmt)
        return result.scalars().one()

    async def edit(self, data: BaseModel, exclude_unset: bool = False, **filter_by) -> None:
        update_stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=exclude_unset))  # Передаем данные для обновления
        )

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
