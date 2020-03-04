from flask_login import current_user, login_required, login_user, logout_user
from flask import jsonify, make_response, redirect, render_template, \
    request, url_for
import datetime
import dateutil.parser
import dateutil.tz
import os

from project import app, db
from project.database.models import User, Company
import project.main.utils as utils
from sqlalchemy import or_

import base64

@app.route('/api/login/', methods=['GET'])
def login():
	email_encripted = request.args.get('email')
	email_decoded = base64.b64decode(email_encripted).decode("utf-8")
	password_encripted = request.args.get('password')
	pass_decoded = base64.b64decode(password_encripted).decode("utf-8")
	user = db.session.query(User).filter_by(email=email_decoded).first()
	if user and user.validatePassword(pass_decoded):
		#Dame el nombre y id del usuario
		username = email_decoded[:email_decoded.find('@')]
		user_id = user.id
		company_id = user.company_id
		#Dame el nombre y id de la compania del usuario
		company_name= db.session.query(Company.name).filter_by(id=company_id).first()
		user_data={}
		user_data['username']=username
		user_data['user_id']=user_id
		user_data['company_name']=company_name[0]
		user_data['company_id']=company_id
		return make_response(jsonify(user_data), 200)
	else:
		return make_response(jsonify('User and password not valid'), 404)





