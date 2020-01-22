from .. import db

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
        
import qairamap.main.model.utils as utils