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


@app.route('/api/get_qhawax_inca/', methods=['GET'])
def getIncaQhawaxInca():
    try:
        name = request.args.get('name')
        inca_qhawax = utils.queryIncaQhawax(db.session,name)
        return inca_qhawax
    except Exception as e:
        print(e)
        return make_response('Invalid format', 400)

@app.route('/api/get_one_qhawax_msb/', methods=['GET'])
def getOneQhawaxMsb():
    all_qhawax = db.session.query(Qhawax.name, Qhawax._location, Qhawax.main_aqi, Qhawax.main_inca).filter(or_(Qhawax.name == 'qH002',
                                                                                                               Qhawax.name == 'qH003',
                                                                                                               Qhawax.name == 'qH004',
                                                                                                               Qhawax.name == 'qH011',)).all()
    qhawax_list = [
        {'name': qhawax.name, 
        'location': qhawax._location,
        'main_aqi': qhawax.main_aqi,
        'main_inca': qhawax.main_inca } for qhawax in all_qhawax]
    return make_response(jsonify(qhawax_list), 200)

@app.route('/api/get_one_qhawax_miraflores/', methods=['GET'])
def getOneQhawaxMiraflores():
    all_qhawax = db.session.query(Qhawax.name, Qhawax._location, Qhawax.main_aqi, Qhawax.main_inca).filter(or_(Qhawax.name == 'qH011')).all()
    qhawax_list = [
        {'name': qhawax.name, 
        'location': qhawax._location,
        'main_aqi': qhawax.main_aqi,
        'main_inca': qhawax.main_inca } for qhawax in all_qhawax]
    return make_response(jsonify(qhawax_list), 200)