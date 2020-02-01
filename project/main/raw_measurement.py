from flask import jsonify, make_response, redirect, render_template, \
    request, url_for
from flask_socketio import join_room
import datetime
import dateutil.parser
import dateutil.tz
import os

from project import app, db, socketio
from project.database.models import Qhawax, RawMeasurement
import project.main.utils as utils
from sqlalchemy import or_

@app.route('/api/dataRaw/', methods=['POST'])
def handleRawData():
    try:
        data_json = request.get_json()
        product_id = data_json['ID']
        data_json = utils.handleTimestampInData(data_json)
        utils.storeRawDataInDB(db.session, data_json)

        data_json['timestamp'] = str(data_json['timestamp'])
        data_json['ID'] = product_id

        socketio.emit('new_data_event', data_json, room=product_id)
        socketio.emit('new_data_summary', data_json)

        return make_response('OK', 200)
    except Exception as e:
        print(e)
        return make_response('Invalid format', 400)

@app.route('/api/raw_measurements/', methods=['GET'])
def getRawMeasurements():
    qhawax_name = request.args.get('name')
    interval_minutes = int(request.args.get('interval_minutes')) \
        if request.args.get('interval_minutes') is not None else 60
    final_timestamp = datetime.datetime.now(dateutil.tz.tzutc())
    initial_timestamp = final_timestamp - datetime.timedelta(minutes=interval_minutes)
    raw_measurements = utils.queryDBRaw(db.session, qhawax_name, initial_timestamp, final_timestamp)

    if raw_measurements is not None:
        raw_measurements_list = [measurement._asdict() for measurement in raw_measurements]
        return make_response(jsonify(raw_measurements_list), 200)
    return make_response(jsonify('Measurements not found'), 404)

@app.route('/api/raw_measurements_period/', methods=['GET'])
def getRawMeasurementsTimePeriod():
    qhawax_name = request.args.get('name')
    initial_timestamp = dateutil.parser.parse(request.args.get('initial_timestamp'))
    final_timestamp = dateutil.parser.parse(request.args.get('final_timestamp'))
    raw_measurements = utils.queryDBRaw(db.session, qhawax_name, initial_timestamp, final_timestamp)
    if raw_measurements is not None:
        raw_measurements_list = [measurement._asdict() for measurement in raw_measurements]
        return make_response(jsonify(raw_measurements_list), 200)
    return make_response(jsonify('Measurements not found'), 404)