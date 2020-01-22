from flask import jsonify, make_response, redirect, render_template, \
    request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_socketio import join_room
import datetime
import dateutil.parser
import dateutil.tz
import os

from project import app, db, socketio
from project.forms import LoginForm
from project.database.models import User, Qhawax, RawMeasurement, ProcessedMeasurement, AirQualityMeasurement
import project.main.utils as utils
from sqlalchemy import or_


@app.route('/api/data/', methods=['POST'])
def handleNewData():
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