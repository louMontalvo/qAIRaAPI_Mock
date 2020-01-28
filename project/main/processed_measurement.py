from flask import jsonify, make_response, redirect, render_template, \
    request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_socketio import join_room
import datetime
import dateutil.parser
import dateutil.tz
import os

from project import app, db, socketio
from project.database.models import Qhawax, ProcessedMeasurement
import project.main.utils as utils
from sqlalchemy import or_


@app.route('/api/dataProcessed/', methods=['POST'])
def handleNewData():
    try:
        data_json = request.get_json()
        product_id = data_json['ID']
        utils.storeProcessedDataInDB(db.session, data_json)
        socketio.emit('new_data_event', data_json, room=product_id)
        socketio.emit('new_data_summary', data_json)
        return make_response('OK', 200)
    except Exception as e:
        print(e)
        return make_response('Invalid format', 400)

#http://0.0.0.0:8888/api/dataProcessed/

@app.route('/api/processed_measurements_realtime/', methods=['GET'])
def getProcessedMeasurementsLastRows():
    lastID = request.args.get('ID')
    qhawax_name = request.args.get('name')
    if(lastID==""):       
        processed_measurements = utils.queryDBRealTimeProcessed(db.session, qhawax_name)
    else:
        processed_measurements = utils.queryDBNextProcessedMeasurement(db.session,qhawax_name,lastID)
    
    lastID = processed_measurements[0].id
    print(lastID)

    if processed_measurements is not None:
        processed_measurements_list = [measurement._asdict() for measurement in processed_measurements]
        return make_response(jsonify(processed_measurements_list), 200)
    return make_response(jsonify('Measurements not found'), 404)

#http://0.0.0.0:8888/api/processed_measurements_realtime/?ID=395153&name=qH011

@app.route('/api/processed_measurements_period/', methods=['GET'])
def getProcessedMeasurementsTimePeriod():
    qhawax_name = request.args.get('name')
    print(qhawax_name)
    initial_timestamp = dateutil.parser.parse(request.args.get('initial_timestamp'))
    final_timestamp = dateutil.parser.parse(request.args.get('final_timestamp'))
    processed_measurements = utils.queryDBProcessed(db.session, qhawax_name, initial_timestamp, final_timestamp)

    if processed_measurements is not None:
        processed_measurements_list = [measurement._asdict() for measurement in processed_measurements]
        averaged_measurements_list = utils.averageMeasurementsInHours(processed_measurements_list, initial_timestamp, final_timestamp, 1)
        return make_response(jsonify(averaged_measurements_list), 200)
    return make_response(jsonify('Measurements not found'), 404)

#http://0.0.0.0:8888/api/processed_measurements_period/?name=qH011&initial_timestamp=Tue, 27 Jan 2020 17:03:58 GMT&final_timestamp=Tue, 28 Jan 2020 17:03:58 GMT
