from server import db


class BaseModel(db.Model):
    """ Base data model for all objects """
    __abstract__ = True

    def __init__(self, *args):
        super().__init__(*args)

    def __repr__(self):
        """Define a base way to print models"""
        return '%s(%s)' % (self.__class__.__name__, {
            column: value
            for column, value in self._to_dict().items()
        })

    def json(self):
        """
                Define a base way to jsonify models, dealing with datetime objects
        """
        return {
            column: value for column, value in self._to_dict().items()
        }


class Apartment(BaseModel):
    """ Model for apartments table """
    __tablename__ = 'tb_apartments'
    id = db.Column("tb_apartment_id", db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    mslApartmentId = db.Column("mls_apartment_id", db.Integer, nullable=False, unique=True, index=True)
    longitude = db.Column("longitude", db.Float, nullable=False)
    latitude = db.Column("latitude", db.Float, nullable=False)
    city = db.Column("city", db.String, nullable=False)
    cityRegion = db.Column("city_region", db.String)
    price = db.Column("price", db.Float, nullable=False)
    distanceToBus = db.Column("distance_to_bus", db.Float)
    distanceToSchool = db.Column("distance_to_school", db.Float)
    distanceToSchoolBus = db.Column("distance_to_school_bus", db.Float)
    distanceToShopping = db.Column("distance_to_shopping", db.Float)
