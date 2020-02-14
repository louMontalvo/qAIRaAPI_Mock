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

from passlib.hash import bcrypt
from project.main.email import sendEmail
from project.response_codes import RESPONSE_CODES


@app.route('/api/get_qhawax_inca/', methods=['GET'])
def getIncaQhawaxInca():
    try:
        name = request.args.get('name')
        inca_qhawax = utils.queryIncaQhawax(db.session,name)
        return inca_qhawax
    except Exception as e:
        print(e)
        return make_response('Invalid format', 400)

@app.route('/api/get_one_qhawax_msb/', methods=['GET'])
def getOneQhawaxMsb():
    all_qhawax = db.session.query(Qhawax.name, Qhawax._location, Qhawax.main_aqi, Qhawax.main_inca).filter(or_(Qhawax.name == 'qH002',
                                                                                                               Qhawax.name == 'qH003',
                                                                                                               Qhawax.name == 'qH004',
                                                                                                               Qhawax.name == 'qH011',)).all()
    qhawax_list = [
        {'name': qhawax.name, 
        'location': qhawax._location,
        'main_aqi': qhawax.main_aqi,
        'main_inca': qhawax.main_inca } for qhawax in all_qhawax]
    return make_response(jsonify(qhawax_list), 200)

@app.route('/api/get_one_qhawax_miraflores/', methods=['GET'])
def getOneQhawaxMiraflores():
    all_qhawax = db.session.query(Qhawax.name, Qhawax._location, Qhawax.main_aqi, Qhawax.main_inca).filter(or_(Qhawax.name == 'qH011')).all()
    qhawax_list = [
        {'name': qhawax.name, 
        'location': qhawax._location,
        'main_aqi': qhawax.main_aqi,
        'main_inca': qhawax.main_inca } for qhawax in all_qhawax]
    return make_response(jsonify(qhawax_list), 200)

@app.route('/api/get_qhawax_msb/', methods=['GET'])
def getQhawaxSanBorja():
    all_qhawax = db.session.query(Qhawax.name, Qhawax._location, Qhawax.main_aqi, Qhawax.main_inca, Qhawax.qhawax_type, Qhawax.state, Qhawax.eca_noise_id).filter(or_(Qhawax.company_id == 4)).all()
    qhawax_list = [
        {'name': qhawax.name, 
        'location': qhawax._location,
        'main_aqi': qhawax.main_aqi,
        'main_inca': qhawax.main_inca,
        'qhawax_type': qhawax.qhawax_type,
        'state':qhawax.state,
        'eca_noise_id': qhawax.eca_noise_id} for qhawax in all_qhawax]
    return make_response(jsonify(qhawax_list), 200)

@app.route('/api/get_qhawax_miraflores/', methods=['GET'])
def getQhawaxMiraflores():
    all_qhawax = db.session.query(Qhawax.name, Qhawax._location, Qhawax.main_aqi, Qhawax.main_inca, Qhawax.qhawax_type, Qhawax.state, Qhawax.eca_noise_id).filter(or_(Qhawax.company_id == 8)).all()
    qhawax_list = [
        {'name': qhawax.name, 
        'location': qhawax._location,
        'main_aqi': qhawax.main_aqi,
        'main_inca': qhawax.main_inca,
        'qhawax_type': qhawax.qhawax_type,
        'state':qhawax.state,
        'eca_noise_id': qhawax.eca_noise_id} for qhawax in all_qhawax]
    return make_response(jsonify(qhawax_list), 200)

@app.route('/api/get_qhawax_cercado/', methods=['GET'])
def getQhawaxCercadoLima():
    all_qhawax = db.session.query(Qhawax.name, Qhawax._location, Qhawax.main_aqi, Qhawax.main_inca, Qhawax.qhawax_type, Qhawax.state, Qhawax.eca_noise_id).filter(or_(Qhawax.company_id == 3)).all()
    qhawax_list = [
        {'name': qhawax.name, 
        'location': qhawax._location,
        'main_aqi': qhawax.main_aqi,
        'main_inca': qhawax.main_inca,
        'qhawax_type': qhawax.qhawax_type,
        'state':qhawax.state,
        'eca_noise_id': qhawax.eca_noise_id} for qhawax in all_qhawax]
    return make_response(jsonify(qhawax_list), 200)

@app.route('/api/get_all_qhawax/', methods=['GET'])
def getAllQhawax():
    all_qhawax = db.session.query(Qhawax.name, Qhawax._location, Qhawax.main_aqi, Qhawax.main_inca,Qhawax.qhawax_type, Qhawax.state, Qhawax.eca_noise_id).order_by(Qhawax.name).all()
    qhawax_list = [
        {'name': qhawax.name, 
        'location': qhawax._location,
        'main_aqi': qhawax.main_aqi,
        'main_inca': qhawax.main_inca,
        'qhawax_type': qhawax.qhawax_type,
        'state':qhawax.state,
        'eca_noise_id': qhawax.eca_noise_id } for qhawax in all_qhawax]
    return make_response(jsonify(qhawax_list), 200)

@app.route('/api/get_all_active_qhawax/', methods=['GET'])
def getActiveQhawax():
    all_active_qhawax = db.session.query(Qhawax.name, Qhawax._location, Qhawax.main_aqi, Qhawax.main_inca,Qhawax.qhawax_type, Qhawax.eca_noise_id).order_by(Qhawax.name).filter((Qhawax.state == 'ON')).all()
    qhawax_list = [
        {'name': qhawax.name, 
        'location': qhawax._location,
        'main_aqi': qhawax.main_aqi,
        'main_inca': qhawax.main_inca,
        'qhawax_type': qhawax.qhawax_type,
        'eca_noise_id': qhawax.eca_noise_id } for qhawax in all_active_qhawax]
    return make_response(jsonify(qhawax_list), 200)

@app.route('/api/save_location/', methods=['POST'])
def saveLocation():
    req_json = request.get_json()
    try:
        qhawax_id = str(req_json['product_id']).strip()
        lat = float(req_json['lat'])
        lon = float(req_json['lon'])
    except KeyError as e:
        json_message = jsonify({'error': 'Parameter \'%s\' is missing in JSON object' % (e)})
        return make_response(json_message, 400)
    
    utils.saveLocationFromProductID(db.session, qhawax_id, lat, lon)
    return make_response('Success', 200)

@app.route('/api/save_main_inca/', methods=['POST'])
def updateIncaData():
    req_json = request.get_json()
    jsonsend={}
    try:
        name = str(req_json['name']).strip()
        data_json = req_json['value_inca']
        utils.updateMainIncaInDB(db.session, data_json, name)
        jsonsend['name'] = name
        jsonsend['value_inca'] =req_json['value_inca']
        socketio.emit('update_inca_event', jsonsend, room=name)
        socketio.emit('update_inca_summary', jsonsend)

        return make_response('OK', 200)
    except Exception as e:
        print(e)
        return make_response('Invalid format. Exception="%s"' % (e), 400)


@app.route('/api/request_all_locations/', methods=['GET'])
def requestAllLocations():
    locations = utils.getAllLocations(db.session)
    return make_response(jsonify(locations), 200)

@app.route('/api/get_time_active_qhawax/', methods=['GET'])
def getQhawaxLatestTimestamp():
    qhawax_name = request.args.get('qhawax_name')
    return utils.getQhawaxLatestTimestamp(db.session, qhawax_name)

@app.route('/api/qhawax_critical_timestamp_alert/', methods=['POST'])
def sendQhawaxTimestamp():
    req_json = request.get_json(cache=False)
    try:
        qhawax_name = str(req_json['qhawax_name']).strip()
        secret_key_hashed = str(req_json['secret_key']).strip()
    except KeyError as e:
        return utils.makeMissingParameterResponse(e.message)

    qhawax = utils.getQhawaxLatestCoordinatesFromName(db.session, qhawax_name)
    timestamp = utils.getQhawaxLatestTimestamp(db.session, qhawax_name)
    lessfive = timestamp - datetime.timedelta(hours=5)
    lessfive = str(lessfive)
    if (lessfive!=None):
        if qhawax is not None and bcrypt.verify(app.config['SECRET_KEY'], secret_key_hashed):
            subject = 'Qhawax %s no se encuentra activo' % (qhawax_name)
            content = 'Ultima vez que se mostró activo: %s' % (lessfive)
            sendEmail(to=app.config['MAIL_DEFAULT_RECEIVER'], subject=subject, template=content)
            json_message = jsonify({'OK': 'Email sent for active qhawax: %s' % (qhawax_name)})
            return make_response(json_message, RESPONSE_CODES['OK'])
        else:
            json_message = jsonify({'error': 'Qhawax not found with name: %s' % (qhawax_name)})
            return make_response(json_message, RESPONSE_CODES['NOT_FOUND'])

@app.route('/api/qhawax_status/', methods=['GET'])
def getQhawaxStatus():
    try:
        name = request.args.get('name')
        qhawax_status = utils.getQhawaxStatus(db.session, name)
        return qhawax_status
    except Exception as e:
        print(e)
        return make_response('Invalid format', 400)

@app.route('/api/qhawax_change_status_off/', methods=['POST'])
def sendQhawaxStatusOff():
    req_json = request.get_json()
    qhawax_id = str(req_json['qhawax_name']).strip()    
    utils.saveStatusOff(db.session, qhawax_id)
    return make_response('Success', 200)


@app.route('/api/qhawax_change_status_on/', methods=['POST'])
def sendQhawaxStatusOn():
    req_json = request.get_json()
    qhawax_id = str(req_json['qhawax_name']).strip()    
    utils.saveStatusOn(db.session, qhawax_id)
    return make_response('Success', 200)


