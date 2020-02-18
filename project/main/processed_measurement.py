from flask import jsonify, make_response, redirect, render_template, \
    request, url_for
from flask_socketio import join_room
import datetime
import dateutil.parser
import dateutil.tz
import os

from project import app, db, socketio
from project.database.models import Qhawax, ProcessedMeasurement
import project.main.utils as utils
from sqlalchemy import or_

@app.route('/api/processed_measurements/', methods=['GET', 'POST'])
def storeProcessedData():
    if request.method == 'GET':
        qhawax_name = request.args.get('name')
        interval_minutes = int(request.args.get('interval_minutes')) \
            if request.args.get('interval_minutes') is not None else 60
        final_timestamp = datetime.datetime.now(dateutil.tz.tzutc())
        initial_timestamp = final_timestamp - datetime.timedelta(minutes=interval_minutes)
        processed_measurements = utils.queryDBProcessed(db.session, qhawax_name, initial_timestamp, final_timestamp)

        if processed_measurements is not None:
            processed_measurements_list = [measurement._asdict() for measurement in processed_measurements]
            return make_response(jsonify(processed_measurements_list), 200)

        else:
            return make_response(jsonify('Measurements not found'), 404)

    if request.method == 'POST':
        try:
            data_json = request.get_json()
            utils.storeProcessedDataInDB(db.session, data_json)
            return make_response('OK', 200)
        except Exception as e:
            print(e)
            return make_response('Invalid format. Exception="%s"' % (e), 400)

@app.route('/api/dataProcessed/', methods=['POST'])
def handleProcessedData():
    try:
        data_json = request.get_json()
        product_id = data_json['ID']
        utils.storeProcessedDataInDB(db.session, data_json)

        data_json['timestamp'] = str(data_json['timestamp'])
        data_json['ID'] = product_id

        socketio.emit('new_data_event_processed', data_json, room=product_id)
        socketio.emit('new_data_summary_processed', data_json)
        return make_response('OK', 200)
    except Exception as e:
        print(e)
        return make_response('Invalid format', 400)

@app.route('/api/processed_measurements_realtime/', methods=['GET'])
def getProcessedMeasurementsLastRows():
    lastID = request.args.get('ID')
    qhawax_name = request.args.get('name')
    if(lastID==""):       
        processed_measurements = utils.queryDBRealTimeProcessed(db.session, qhawax_name)
    else:
        processed_measurements = utils.queryDBNextProcessedMeasurement(db.session,qhawax_name,lastID)
    
    lastID = processed_measurements[0].id

    if processed_measurements is not None:
        processed_measurements_list = [measurement._asdict() for measurement in processed_measurements]
        return make_response(jsonify(processed_measurements_list), 200)
    return make_response(jsonify('Measurements not found'), 404)


@app.route('/api/average_processed_measurements_period/', methods=['GET'])
def getAverageProcessedMeasurementsTimePeriod():
    qhawax_name = request.args.get('name')
    initial_timestamp = dateutil.parser.parse(request.args.get('initial_timestamp'))
    final_timestamp = dateutil.parser.parse(request.args.get('final_timestamp'))
    processed_measurements = utils.queryDBProcessed(db.session, qhawax_name, initial_timestamp, final_timestamp)

    if processed_measurements is not None:
        processed_measurements_list = [measurement._asdict() for measurement in processed_measurements]
        averaged_measurements_list = utils.averageMeasurementsInHours(processed_measurements_list, initial_timestamp, final_timestamp, 1)
        return make_response(jsonify(averaged_measurements_list), 200)
    return make_response(jsonify('Measurements not found'), 404)

@app.route('/api/processed_measurements_period/', methods=['GET'])
def getProcessedMeasurementsTimePeriod():
    qhawax_name = request.args.get('name')
    initial_timestamp = dateutil.parser.parse(request.args.get('initial_timestamp'))
    final_timestamp = dateutil.parser.parse(request.args.get('final_timestamp'))
    processed_measurements = utils.queryDBProcessed(db.session, qhawax_name, initial_timestamp, final_timestamp)

    if processed_measurements is not None:
        processed_measurements_list = [measurement._asdict() for measurement in processed_measurements]
        return make_response(jsonify(processed_measurements_list), 200)
    return make_response(jsonify('Measurements not found'), 404)
