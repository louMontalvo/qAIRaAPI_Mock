from .. import db
from passlib.hash import bcrypt

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

import qairamap.main.model.utils as utils