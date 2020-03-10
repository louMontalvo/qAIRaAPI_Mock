from flask import jsonify, make_response, redirect, render_template, \
    request, url_for

import datetime
import dateutil.parser
import dateutil.tz
import os

from project import app, db, socketio
from project.database.models import Qhawax
import project.main.utils as utils
from sqlalchemy import or_
from flask_socketio import join_room

@app.route('/api/newQhawaxInstallation/', methods=['POST'])
def newQhawaxInstallation():
    try:
        data_json = request.get_json()
        qhawax_id = data_json['qhawax_id']
        utils.storeNewQhawaxInstallation(db.session, data_json)
        utils.setOccupiedQhawax(db.session,qhawax_id)
        return make_response('OK', 200)
    except Exception as e:
        print(e)
        return make_response('Invalid format', 400)

@app.route('/api/saveEndWorkField/', methods=['POST'])
def saveEndWorkField():
    try:
        data_json = request.get_json()
        qhawax_id = data_json['qhawax_id']
        utils.saveEndWorkFieldDate(db.session, data_json['id'],data_json['end_date'])
        utils.setAvailableQhawax(db.session,qhawax_id)
        return make_response('OK', 200)
    except Exception as e:
        print(e)
        return make_response('Invalid format', 400)

@app.route('/api/AllQhawaxInField/', methods=['GET'])
def getAllQhawaxInField():
    qhawax_in_field = utils.queryQhawaxInField(db.session)

    if qhawax_in_field is not None:
        qhawax_in_field_list = [installation._asdict() for installation in qhawax_in_field]
        qhawax_in_field_list= utils.getCompanyName(db.session, qhawax_in_field_list)
        return make_response(jsonify(qhawax_in_field_list), 200)
    else:
        return make_response(jsonify('Qhawax in Field not found'), 404)

@app.route('/api/AllQhawaxByCompany/', methods=['GET'])
def getQhawaxByCompany():
    company_id = request.args.get('company_id')
    #Sino solo traer los qhawax de dicha compañia
    qhawax_in_field_by_company = utils.queryQhawaxInFieldByCompany(db.session, company_id)
    if qhawax_in_field_by_company is not None:
        qhawax_in_field_by_company_list = [installation._asdict() for installation in qhawax_in_field_by_company]
        qhawax_in_field_by_company_list= utils.getQhawaxDetail(db.session, qhawax_in_field_by_company_list)
        return make_response(jsonify(qhawax_in_field_by_company_list), 200)
    else:
        return make_response(jsonify('Qhawax By Company not found'), 404)

@app.route('/api/AllAvailableQhawax/', methods=['GET'])
def getAvailableQhawax():
    available_qhawax = db.session.query(Qhawax.id, Qhawax.name, Qhawax.qhawax_type, Qhawax.state).order_by(Qhawax.name).filter_by(availability='Available').all()
    qhawax_list = [
        {'name': qhawax.name, 
        'qhawax_type': qhawax.qhawax_type,
        'state': qhawax.state,
        'id': qhawax.id} for qhawax in available_qhawax]
    return make_response(jsonify(qhawax_list), 200)

@app.route('/api/AllQhawaxRecord/', methods=['GET'])
def getAllQhawaxRecord():
    qhawax_id = request.args.get('qhawax_id')
    all_qhawax_record = utils.queryQhawaxRecord(db.session, qhawax_id)
    if all_qhawax_record is not None:
        all_qhawax_record_list = [installation._asdict() for installation in all_qhawax_record]
        return make_response(jsonify(all_qhawax_record_list), 200)
    else:
        return make_response(jsonify('Qhawax Record not found'), 404)

@app.route('/api/QhawaxInstallationDetail/', methods=['GET'])
def getQhawaxInstallationDetail():
    installation_id = request.args.get('installation_id')
    qhawax_detail = utils.queryQhawaxInstallationDetail(db.session, installation_id)
    if qhawax_detail is not None:
        detail_list = [detail._asdict() for detail in qhawax_detail]
        return make_response(jsonify(detail_list), 200)
    else:
        return make_response(jsonify('Qhawax Detail not found'), 404)

@app.route('/api/DatesofActiveQhawax/', methods=['GET'])
def getDatesofActiveQhawax():
    qhawax_dates = utils.queryDateOfActiveQhawax(db.session)
    if qhawax_dates is not None:
        qhawax_dates_list = [dates._asdict() for dates in qhawax_dates]
        return make_response(jsonify(qhawax_dates_list), 200)
    else:
        return make_response(jsonify('Qhawax Dates not found'), 404)






