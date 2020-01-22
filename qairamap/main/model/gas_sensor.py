from .. import db

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
            'sensitivity': self.sensitivity
        }