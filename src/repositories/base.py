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

    async def edit(self, data: BaseModel, **filter_by):
        put_data_stmt = (
            update(self.model)
            .values(**data.model_dump())  # Передаем данные для обновления
            .returning(self.model)  # Возвращаем обновленную запись
            .filter_by(**filter_by)  # Применяем фильтрацию по ID или другим критериям
        )

        # Выполняем запрос
        result = await self.session.execute(put_data_stmt)

        # Получаем обновленные данные
        updated_hotel = result.scalars().one_or_none()

        # Если не найден отель с заданными параметрами, выбрасываем исключение
        if not updated_hotel:
            raise HTTPException(status_code=404, detail="Hotel not found")

        return updated_hotel

    async def delete(self, data: BaseModel, **filter_by):
        ...
