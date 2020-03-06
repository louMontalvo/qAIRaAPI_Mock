from flask import jsonify, make_response, redirect, render_template, \
    request, url_for
import datetime
import dateutil.parser
import dateutil.tz
import os

from project import app, db, socketio
from project.database.models import Company
import project.main.utils as utils
from sqlalchemy import or_



@app.route('/api/get_all_company/', methods=['GET'])
def getAllCompany():
	allCompanies = utils.queryGetCompanies(db.session)
	if allCompanies is not None:
		allCompanies_list = [
        {'name': company.name,
        'id': company.id} for company in allCompanies]
		return make_response(jsonify(allCompanies_list), 200)
	return make_response(jsonify('Companies not found'), 404)