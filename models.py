from server import db
from sqlalchemy import inspect


class BaseModel(db.Model):
    """ Base data model for all objects """
    __abstract__ = True

    def __init__(self, *args):
        super().__init__(*args)

    def __repr__(self):
        """Define a base way to print models"""
        return '%s%s' % (self.__class__.__name__,
                         self.json())

    def json(self):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.Column_attrs}


class Apartment(BaseModel):
    """ Model for apartments table """
    __tablename__ = 'tb_apartments'
    id = db.Column("tb_apartment_id", db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    city = db.Column('city', db.String, nullable=True)
    city_region = db.Column('city_region', db.String, nullable=True)
    country = db.Column('country', db.String, nullable=True)
    picture_url = db.Column('picture_url', db.String, nullable=True)
    size_square_feet = db.Column('size_square_feet', db.String, nullable=True)
    price = db.Column('price', db.Float, nullable=True)
    latitude = db.Column('latitude', db.Float, nullable=True)
    longitude = db.Column('longitude', db.Float, nullable=True)
    address = db.Column('address', db.String, nullable=True)
    leasing_available = db.Column('leasing_available', db.Boolean, nullable=True)
    dist_to_closest_cinema = db.Column('dist_to_closest_cinema', db.Float, nullable=True)
    num_of_cinemas = db.Column('num_of_cinemas', db.Integer, nullable=True)
    dist_to_closest_cafe = db.Column('dist_to_closest_cafe', db.Float, nullable=True)
    num_of_cafes = db.Column('num_of_cafes', db.Integer, nullable=True)
    dist_to_closest_pub = db.Column('dist_to_closest_pub', db.Float, nullable=True)
    num_of_pubs = db.Column('num_of_pubs', db.Integer, nullable=True)
    dist_to_closest_restaurant = db.Column('dist_to_closest_restaurant', db.Float, nullable=True)
    num_of_restaurants = db.Column('num_of_restaurants', db.Integer, nullable=True)
    dist_to_closest_cafe_rest = db.Column('dist_to_closest_cafe_rest', db.Float, nullable=True)
    num_of_cafes_rests = db.Column('num_of_cafes_rests', db.Integer, nullable=True)
    dist_to_closest_park = db.Column('dist_to_closest_park', db.Float, nullable=True)
    num_of_parks = db.Column('num_of_parks', db.Integer, nullable=True)
    dist_to_closest_railway_station = db.Column('dist_to_closest_railway_station', db.Float, nullable=True)
    num_of_railway_stations = db.Column('num_of_railway_stations', db.Integer, nullable=True)
    dist_to_closest_highway = db.Column('dist_to_closest_highway', db.Float, nullable=True)
    num_of_highways = db.Column('num_of_highways', db.Integer, nullable=True)
