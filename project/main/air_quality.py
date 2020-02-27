from flask import jsonify, make_response, redirect, render_template, \
    request, url_for
from flask_socketio import join_room
import datetime
import dateutil.parser
import dateutil.tz
import os

from project import app, db, socketio
from project.database.models import Qhawax, ProcessedMeasurement, AirQualityMeasurement
import project.main.utils as utils
from sqlalchemy import or_


@app.route('/api/air_quality_measurements/', methods=['GET', 'POST'])
def storeAirQualityData():
    if request.method == 'GET':
        qhawax_name = request.args.get('name')
        interval_hours = int(request.args.get('interval_hours')) \
            if request.args.get('interval_hours') is not None else 1
        final_timestamp = datetime.datetime.now(dateutil.tz.tzutc()) - datetime.timedelta(hours=5)
        initial_timestamp = final_timestamp - datetime.timedelta(hours=interval_hours)
        air_quality_measurements = utils.queryDBAirQuality(db.session, qhawax_name, initial_timestamp, final_timestamp)

        if air_quality_measurements is not None:
            air_quality_measurements_list = [measurement._asdict() for measurement in air_quality_measurements]
            return make_response(jsonify(air_quality_measurements_list), 200)
        else:
            return make_response(jsonify('Measurements not found'), 404)

    if request.method == 'POST':
        try:
            data_json = request.get_json()
            utils.storeAirQualityDataInDB(db.session, data_json)
            return make_response('OK', 200)
        except Exception as e:
            print(e)
            return make_response('Invalid format. Exception="%s"' % (e), 400)

@app.route('/api/air_quality_measurements_period/', methods=['GET'])
def getAirQualityMeasurementsTimePeriod():
    qhawax_name = request.args.get('name')
    initial_timestamp = dateutil.parser.parse(request.args.get('initial_timestamp'))
    final_timestamp = dateutil.parser.parse(request.args.get('final_timestamp'))
    air_quality_measurements = utils.queryDBAirQuality(db.session, qhawax_name, initial_timestamp, final_timestamp)

    if air_quality_measurements is not None:
        air_quality_measurements_list = [measurement._asdict() for measurement in air_quality_measurements]
        return make_response(jsonify(air_quality_measurements_list), 200)
    else:
        return make_response(jsonify('Measurements not found'), 404)

@app.route('/api/gas_average_measurement/', methods=['GET'])
def getGasAverageMeasurementsEvery24():
    qhawax_name = request.args.get('qhawax')
    gas_name = request.args.get('gas')
    gas_average_measurement = utils.queryDBGasAverageMeasurement(db.session, qhawax_name, gas_name)

    if gas_average_measurement is not None:
        gas_average_measurement_list = [measurement._asdict() for measurement in gas_average_measurement]
        return make_response(jsonify(gas_average_measurement_list), 200)
    else:
        return make_response(jsonify('Measurements not found'), 404)