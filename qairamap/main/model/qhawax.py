from .. import db
from sqlalchemy_json import NestedMutableJson

class Qhawax(db.Model):
    __tablename__ = 'qhawax'

    # Column's definition
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    name = db.Column(db.String(300), nullable=False, unique=True)
    main_aqi = db.Column(db.Float)
    main_inca = db.Column(db.Float)
    _location = db.Column(NestedMutableJson) # Location object
    raw_measurements = db.relationship('RawMeasurement', backref='qhawax', lazy='subquery',
                                        cascade='delete, delete-orphan')
    processed_measurements = db.relationship('ProcessedMeasurement', backref='qhawax', lazy='subquery',
                                                cascade='delete, delete-orphan')
    air_quality_measurements = db.relationship('AirQualityMeasurement', backref='qhawax', lazy='subquery',
                                                cascade='delete, delete-orphan')
    gas_sensors = db.relationship('GasSensor', backref='qhawax', lazy='subquery') # Don't delete gas sensor if qhawax is deleted

    def __init__(self, company, name, location):
        utils.checkValidCompany(company)
        self.company = company
        self.name = name
        self.location = location

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, location):
        utils.checkValidLocation(location)
        self._location = location.serialize

    @property
    def serialize(self):
        return {
            'name' : self.name,
        'location' : self.location,
        'main_aqi' : self.main_aqi,
       'main_inca' : self.main_inca }

import qairamap.main.model.utils as utils