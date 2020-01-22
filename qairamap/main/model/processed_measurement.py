from .. import db, flask_bcrypt

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