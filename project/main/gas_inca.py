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