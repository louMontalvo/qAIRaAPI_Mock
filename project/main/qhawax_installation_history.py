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
        print(data_json)
        utils.storeNewQhawaxInstallation(db.session, data_json)
        return make_response('OK', 200)
    except Exception as e:
        print(e)
        return make_response('Invalid format', 400)


@app.route('/api/saveEndWorkField/', methods=['POST'])
def saveEndWorkField():
    try:
        data_json = request.get_json()
        utils.saveEndWorkFieldDate(db.session, data_json['id'],data_json['end_date'])
        return make_response('OK', 200)
    except Exception as e:
        print(e)
        return make_response('Invalid format', 400)

@app.route('/api/AllQhawaxInField/', methods=['GET'])
def getAllQhawaxInField():
    qhawax_in_field = utils.queryQhawaxInField(db.session)

    if qhawax_in_field is not None:
        qhawax_in_field_list = [installation._asdict() for installation in qhawax_in_field]
        return make_response(jsonify(qhawax_in_field_list), 200)

    else:
        return make_response(jsonify('Measurements not found'), 404)