from src.models.bookings import BookingOrm
from src.models.facilities import FacilitiesOrm
from src.models.hotels import HotelsORM
from src.models.rooms import RoomsORM
from src.models.users import UsersOrm
from src.repositories.mappers.base import DataMapper
from src.schemas.bookings import Booking
from src.schemas.facilities import Facility
from src.schemas.hotels import Hotel
from src.schemas.rooms import Room, RoomWithRels
from src.schemas.users import User


class HotelDataMapper(DataMapper):
    db_model = HotelsORM
    schema = Hotel


class RoomDataMapper(DataMapper):
    db_model = RoomsORM
    schema = Room


class RoomDataWithRelsMapper(DataMapper):
    db_model = RoomsORM
    schema = RoomWithRels


class UserDataMapper(DataMapper):
    db_model = UsersOrm
    schema = User


class BookingDataMapper(DataMapper):
    db_model = BookingOrm
    schema = Booking


class FacilityDataMapper(DataMapper):
    db_model = FacilitiesOrm
    schema = Facility
