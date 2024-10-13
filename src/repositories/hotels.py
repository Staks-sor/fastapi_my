from sqlalchemy import select, func

from src.models.hotels import HotelsORM
from src.repositories.base import BaseRepository


class HotelsRepository(BaseRepository):
    model = HotelsORM

    async def get_all(
            self,
            location,
            title,
            limit,
            offset,
    ):
        query = select(HotelsORM)
        if location:
            query = query.filter(func.lower(HotelsORM.location).contains(func.lower(location.strip())))
        if title:
            query = query.filter(func.lower(HotelsORM.title).contains(func.lower(title.strip())))

        query = (
            query
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)

        return result.scalars().all()

    async def add(
            self,
            location,
            title,
    ):

        new_hotel = HotelsORM(location=location, title=title)

        # Добавляем новый объект в сессию
        self.session.add(new_hotel)

