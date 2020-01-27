from flask import jsonify, make_response, redirect, render_template, \
    request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_socketio import join_room
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
    print('Entre a requestOffsets')
    qhawax_id = request.args.get('ID')
    print(qhawax_id)
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

#http://0.0.0.0:8888/api/request_offsets/?ID=qH006
#http://0.0.0.0:8888/api/request_controlled_offsets/?ID=qH006
#http://0.0.0.0:8888/api/request_non_controlled_offsets/?ID=qH006


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


