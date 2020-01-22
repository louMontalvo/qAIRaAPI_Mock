from .. import db, flask_bcrypt

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