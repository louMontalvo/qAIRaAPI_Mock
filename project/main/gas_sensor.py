from flask import jsonify, make_response, redirect, render_template, \
    request, url_for
import datetime
import dateutil.parser
import dateutil.tz
import os

from project import app, db, socketio
from project.database.models import Qhawax, GasSensor
import project.main.utils as utils
from sqlalchemy import or_


@app.route('/api/request_offsets/', methods=['GET'])
def requestOffsets():
    qhawax_id = request.args.get('ID')
    offsets = utils.getOffsetsFromProductID(db.session, qhawax_id)
    return make_response(jsonify(offsets), 200)

@app.route('/api/request_controlled_offsets/', methods=['GET'])
def requestControlledOffsets():
    qhawax_id = request.args.get('ID')
    controlled_offsets = utils.getControlledOffsetsFromProductID(db.session, qhawax_id)
    return make_response(jsonify(controlled_offsets), 200)

@app.route('/api/request_non_controlled_offsets/', methods=['GET'])
def requestNonControlledOffsets():
    qhawax_id = request.args.get('ID')
    non_controlled_offsets = utils.getNonControlledOffsetsFromProductID(db.session, qhawax_id)
    return make_response(jsonify(non_controlled_offsets), 200)

@app.route('/api/save_offsets/', methods=['POST'])
def saveOffsets():
    req_json = request.get_json()
    try:
        qhawax_id = str(req_json['product_id']).strip()
        offsets = req_json['offsets']
    except KeyError as e:
        json_message = jsonify({'error': 'Parameter \'%s\' is missing in JSON object' % (e)})
        return make_response(json_message, 400)
    
    utils.saveOffsetsFromProductID(db.session, qhawax_id, offsets)
    return make_response('Success', 200)

@app.route('/api/save_controlled_offsets/', methods=['POST'])
def saveControlledOffsets():
    req_json = request.get_json()
    try:
        qhawax_id = str(req_json['product_id']).strip()
        controlled_offsets = req_json['controlled_offsets']
    except KeyError as e:
        json_message = jsonify({'error': 'Parameter \'%s\' is missing in JSON object' % (e)})
        return make_response(json_message, 400)

    utils.saveControlledOffsetsFromProductID(db.session, qhawax_id, controlled_offsets)
    return make_response('Success', 200)

@app.route('/api/save_non_controlled_offsets/', methods=['POST'])
def saveNonControlledOffsets():
    req_json = request.get_json()
    try:
        qhawax_id = str(req_json['product_id']).strip()
        non_controlled_offsets = req_json['non_controlled_offsets']
    except KeyError as e:
        json_message = jsonify({'error': 'Parameter \'%s\' is missing in JSON object' % (e)})
        return make_response(json_message, 400)

    utils.saveNonControlledOffsetsFromProductID(db.session, qhawax_id, non_controlled_offsets)
    return make_response('Success', 200)

@app.route('/api/measurementPromedio/', methods=['GET'])
def requestProm():
    name = request.args.get('name')
    sensor = request.args.get('sensor')
    hoursSensor = request.args.get('hoursSensor')
    final_timestamp = datetime.datetime.now() - datetime.timedelta(hours=5)
    initial_timestamp = final_timestamp - datetime.timedelta(hours=int(hoursSensor))
    qhawax_measurement_sensor = utils.queryDBPROM(db.session, name, sensor, initial_timestamp, final_timestamp)
    return str(qhawax_measurement_sensor)

