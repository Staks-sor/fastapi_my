from datetime import datetime, date

# Импорт гибридного свойства для создания свойств, которые можно использовать как в Python, так и в SQL-запросах.
from sqlalchemy.ext.hybrid import hybrid_property

# Импорт аннотации Mapped для типизации столбцов в модели и mapped_column для описания колонок таблицы.
from sqlalchemy.orm import Mapped, mapped_column

# Импорт ForeignKey для связи между таблицами (внешний ключ).
from sqlalchemy import ForeignKey

# Импорт базового класса модели, от которого наследуются все таблицы.
from src.database import Base


class BookingOrm(Base):  # Определение класса модели для таблицы "bookings".
    __tablename__ = "bookings"  # Имя таблицы в базе данных.

    # Уникальный идентификатор записи (первичный ключ).
    id: Mapped[int] = mapped_column(primary_key=True)

    # Внешний ключ, указывающий на идентификатор пользователя в таблице "users".
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Внешний ключ, указывающий на идентификатор комнаты в таблице "rooms".
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))

    # Дата начала бронирования.
    date_from: Mapped[date]

    # Дата окончания бронирования.
    date_to: Mapped[date]

    # Стоимость бронирования за один день.
    price: Mapped[int]

    @hybrid_property  # Гибридное свойство, которое можно использовать в Python-коде и в SQL-запросах.
    def total_cost(self) -> int:
        # Вычисляет общую стоимость бронирования как произведение цены на количество дней.
        return self.price * (self.date_to - self.date_from).days
