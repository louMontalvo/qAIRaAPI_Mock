from project import db

from passlib.hash import bcrypt
from sqlalchemy_json import NestedMutableJson

class Company(db.Model):
    __tablename__ = 'company'

    # Column's definition
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False, unique=True)
    email_group = db.Column(db.String(300), nullable=False, unique=True)
    users = db.relationship('User', backref='company', lazy='subquery',
                            cascade='delete, delete-orphan')
    qhawaxes = db.relationship('Qhawax', backref='company', lazy='subquery',
                             cascade='delete, delete-orphan')

    def __init__(self, name, email_group):
        utils.checkValidEmailGroup(email_group)
        self.name = name
        self.email_group = email_group

    @property
    def serialize(self):
        return {'name': self.name, 'email_group': self.email_group}

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    authenticated = db.Column(db.Boolean, default=False) # Flask-Login
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    confirmed = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(300), nullable=False, unique=True)
    password_hash = db.Column(db.String(300), nullable=False)

    def __init__(self, company, email, password, confirmed=False):
        utils.checkValidCompany(company)
        utils.checkPasswordLength(password)
        utils.checkEmailIsFromCompany(email, company)
        
        self.company = company
        self.confirmed = confirmed
        self.email = email
        self.password_hash = bcrypt.encrypt(password)

    def changePassword(self, new_password):
        self.password_hash = bcrypt.encrypt(new_password)
    
    def validatePassword(self, password):
        return bcrypt.verify(password, self.password_hash)

    # Methods required for Flask-Login

    def is_active(self):
        return True

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False
    
    @property
    def serialize(self):
        return {'email': self.email}

class Qhawax(db.Model):
    __tablename__ = 'qhawax'

    # Column's definition
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    name = db.Column(db.String(300), nullable=False, unique=True)
    main_aqi = db.Column(db.Float)
    main_inca = db.Column(db.Float)
    type = db.Column(db.String(100), nullable=False, unique=True)
    state = db.Column(db.String(5), nullable=False, unique=True)
    _location = db.Column(NestedMutableJson) # Location object
    raw_measurements = db.relationship('RawMeasurement', backref='qhawax', lazy='subquery',
                                        cascade='delete, delete-orphan')
    processed_measurements = db.relationship('ProcessedMeasurement', backref='qhawax', lazy='subquery',
                                                cascade='delete, delete-orphan')
    air_quality_measurements = db.relationship('AirQualityMeasurement', backref='qhawax', lazy='subquery',
                                                cascade='delete, delete-orphan')
    gas_sensors = db.relationship('GasSensor', backref='qhawax', lazy='subquery') # Don't delete gas sensor if qhawax is deleted

    def __init__(self, company, name, location, type,state):
        utils.checkValidCompany(company)
        self.company = company
        self.name = name
        self.location = location
        self.type = type
        self.state = state

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
       'main_inca' : self.main_inca,
       'type'      : self.type,
       'state'     : self.state }

class GasSensor(db.Model):
    __tablename__ = 'gas_sensor'

    # Column's definition
    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.String(100), nullable=False, unique=True)
    purchase_date = db.Column(db.DateTime)
    type = db.Column(db.String(100))
    WE = db.Column(db.Float)
    AE = db.Column(db.Float)
    sensitivity = db.Column(db.Float)
    sensitivity_2 = db.Column(db.Float)
    C2 = db.Column(db.Float, nullable=False, default=0, server_default='0')
    C1 = db.Column(db.Float, nullable=False, default=1, server_default='1')
    C0 = db.Column(db.Float, nullable=False, default=0, server_default='0')
    NC1 = db.Column(db.Float, nullable=False, default=1, server_default='1')
    NC0 = db.Column(db.Float, nullable=False, default=0, server_default='0')
    qhawax_id = db.Column(db.Integer, db.ForeignKey('qhawax.id'))

    @property
    def serialize(self):
        return {
            'serial_number': self.serial_number,
            'purchase_date': str(self.timestamp),
            'type': self.type,
            'WE': self.WE,
            'AE': self.AE,
            'sensitivity': self.sensitivity,
            'sensitivity_2': self.sensitivit_2
        }

class RawMeasurement(db.Model):
    __tablename__ = 'raw_measurement'

    # Column's definition
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    CO_OP1 = db.Column(db.Float)
    CO_OP2 = db.Column(db.Float)
    CO2 = db.Column(db.Float)
    H2S_OP1 = db.Column(db.Float)
    H2S_OP2 = db.Column(db.Float)
    NO_OP1 = db.Column(db.Float)
    NO_OP2 = db.Column(db.Float)
    NO2_OP1 = db.Column(db.Float)
    NO2_OP2 = db.Column(db.Float)
    O3_OP1 = db.Column(db.Float)
    O3_OP2 = db.Column(db.Float)
    PM1 = db.Column(db.Float)
    PM25 = db.Column(db.Float)
    PM10 = db.Column(db.Float)
    SO2_OP1 = db.Column(db.Float)
    SO2_OP2 = db.Column(db.Float)
    VOC_OP1 = db.Column(db.Float)
    VOC_OP2 = db.Column(db.Float)
    UV = db.Column(db.Float)
    UVA = db.Column(db.Float)
    UVB = db.Column(db.Float)
    spl = db.Column(db.Float)
    humidity = db.Column(db.Float)
    pressure = db.Column(db.Float)
    temperature = db.Column(db.Float)
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    alt = db.Column(db.Float)
    qhawax_id = db.Column(db.Integer, db.ForeignKey('qhawax.id'))

    @property
    def serialize(self):
        return {
            'ID': self.qhawax.name,
            'timestamp': str(self.timestamp),
            'CO_OP1': self.CO_OP1,
            'CO_OP2': self.CO_OP2,
            'CO2': self.CO2,
            'H2S_OP1': self.H2S_OP1,
            'H2S_OP2': self.H2S_OP2,
            'NO_OP1': self.NO_OP1,
            'NO_OP2': self.NO_OP2,
            'NO2_OP1': self.NO2_OP1,
            'NO2_OP2': self.NO2_OP2,
            'O3_OP1': self.O3_OP1,
            'O3_OP2': self.O3_OP2,
            'PM1': self.PM1,
            'PM25': self.PM25,
            'PM10': self.PM10,
            'SO2_OP1': self.SO2_OP1,
            'SO2_OP2': self.SO2_OP2,
            'VOC_OP1': self.VOC_OP1,
            'VOC_OP2': self.VOC_OP2,
            'UV': self.UV,
            'UVA': self.UVA,
            'UVB': self.UVB,
            'spl': self.spl,
            'humidity': self.humidity,
            'pressure': self.pressure,
            'temperature': self.temperature,
            'lat': self.lat,
            'lon': self.lon,
            'alt': self.alt}


class ProcessedMeasurement(db.Model):
    __tablename__ = 'processed_measurement'

    # Column's definition
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    CO = db.Column(db.Float)
    CO2 = db.Column(db.Float)
    H2S = db.Column(db.Float)
    NO = db.Column(db.Float)
    NO2 = db.Column(db.Float)
    O3 = db.Column(db.Float)
    PM1 = db.Column(db.Float)
    PM25 = db.Column(db.Float)
    PM10 = db.Column(db.Float)
    SO2 = db.Column(db.Float)
    VOC = db.Column(db.Float)
    UV = db.Column(db.Float)
    UVA = db.Column(db.Float)
    UVB = db.Column(db.Float)
    spl = db.Column(db.Float)
    humidity = db.Column(db.Float)
    pressure = db.Column(db.Float)
    temperature = db.Column(db.Float)
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    alt = db.Column(db.Float)
    qhawax_id = db.Column(db.Integer, db.ForeignKey('qhawax.id'))

    @property
    def serialize(self):
        return {
            'timestamp': str(self.timestamp),
            'CO': self.CO,
            'CO2': self.CO2,
            'H2S': self.H2S,
            'NO': self.NO,
            'NO2': self.NO2,
            'O3': self.O3,
            'PM1': self.PM1,
            'PM25': self.PM25,
            'PM10': self.PM10,
            'SO2': self.SO2,
            'VOC': self.VOC,
            'UV': self.UV,
            'UVA': self.UVA,
            'UVB': self.UVB,
            'spl': self.spl,
            'humidity': self.humidity,
            'pressure': self.pressure,
            'temperature': self.temperature,
            'lat': self.lat,
            'lon': self.lon,
            'alt': self.alt}


class AirQualityMeasurement(db.Model):
    __tablename__ = 'air_quality_measurement'

    # Column's definition
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    CO = db.Column(db.Float)
    H2S = db.Column(db.Float)
    NO2 = db.Column(db.Float)
    O3 = db.Column(db.Float)
    PM25 = db.Column(db.Float)
    PM10 = db.Column(db.Float)
    SO2 = db.Column(db.Float)
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    alt = db.Column(db.Float)
    qhawax_id = db.Column(db.Integer, db.ForeignKey('qhawax.id'))

import project.database.utils as utils
