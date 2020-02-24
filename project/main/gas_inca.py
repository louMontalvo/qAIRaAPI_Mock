from flask import jsonify, make_response, redirect, render_template, \
    request, url_for
import datetime
import dateutil.parser
import dateutil.tz
import os

from project import app, db, socketio
from project.database.models import EcaNoise
import project.main.utils as utils
from sqlalchemy import or_

@app.route('/api/saveGasInca/', methods=['POST'])
def handleGasInca():
    try:
        data_json = request.get_json()
        utils.storeGasIncaInDB(db.session, data_json)
        socketio.emit('gas_inca_summary', data_json)
        return make_response('OK', 200)
    except Exception as e:
        print(e)
        return make_response('Invalid format', 400)

@app.route('/api/last_gas_inca_data/', methods=['GET'])
def getLastGasIncaData():
	final_timestamp_gases = datetime.datetime.now(dateutil.tz.tzutc()) - datetime.timedelta(hours=5)
	initial_timestamp_gases = final_timestamp_gases - datetime.timedelta(hours=1)

	gas_inca_last_data = utils.queryDBGasInca(db.session, initial_timestamp_gases, final_timestamp_gases)

	if gas_inca_last_data is not None:
		gas_inca_last_data_list = [measurement._asdict() for measurement in gas_inca_last_data]
		return make_response(jsonify(gas_inca_last_data_list), 200)
	else:
		return make_response(jsonify('Gas Inca not found'), 404)