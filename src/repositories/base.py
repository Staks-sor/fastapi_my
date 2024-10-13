from sqlalchemy import select


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

    async def add(self, *args, **kwargs):
        new_hotel = self.model(**kwargs)
        self.session.add(new_hotel)
        await self.session.commit()
        await self.session.refresh(new_hotel)  # Обновляем объект, чтобы получить его актуальные данные из базы
        return new_hotel