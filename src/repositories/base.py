from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import select, insert, update, delete


class BaseRepository:
    model = None

    def __init__(self, session):
        self.session = session

    async def get_all(self, *args, **kwargs):
        query = select(self.model)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_one_or_none(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def add(self, data: BaseModel):
        add_data_stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        result = await self.session.execute(add_data_stmt)
        return result.scalars().one()

    async def edit(self, data: BaseModel, **filter_by) -> None:
        update_stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump())  # Передаем данные для обновления
        )
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        hotel = result.scalars().one_or_none()

        # Если объект не найден, выбрасываем исключение 404
        if hotel is None:
            raise HTTPException(status_code=404, detail="Hotel not found")
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
