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

@app.route('/api/processed_measurements_realtime/', methods=['GET'])
def getProcessedMeasurements():
    qhawax_name = request.args.get('name')
    print(qhawax_name)
    processed_measurements = utils.queryDBRealTimeProcessed(db.session, qhawax_name)

    if processed_measurements is not None:
        processed_measurements_list = [measurement._asdict() for measurement in processed_measurements]
        return make_response(jsonify(processed_measurements_list), 200)
    return make_response(jsonify('Measurements not found'), 404)

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