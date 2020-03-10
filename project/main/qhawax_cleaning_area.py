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

from passlib.hash import bcrypt
from project.main.email import sendEmail
from project.response_codes import RESPONSE_CODES


@app.route('/api/qhawax_notify_qhawax_cleaning_area/', methods=['POST'])
def sendQhawaxCleaningAreaNotifyTimestamp():
    req_json = request.get_json(cache=False)
    try:
        installation_id = str(req_json['installation_id']).strip()
        comercial_name = str(req_json['comercial_name']).strip()
        type_date = str(req_json['type_date']).strip()
        secret_key_hashed = str(req_json['secret_key']).strip()
    except KeyError as e:
        return utils.makeMissingParameterResponse(e.message)
    content = ''
    date =''
    if installation_id is not None and bcrypt.verify(app.config['SECRET_KEY'], secret_key_hashed):
        subject = 'Limpieza de la Zona en %s' % (comercial_name)
        if(type_date =='Instalacion'):
            date = utils.getInstallationQhawaxDate(db.session,installation_id)
            content = 'Fecha de Instalacion: %s \n Qhawax listo para su primera limpieza de zona' % (date)
        elif (type_date =='Zona'):
            date = utils.getCleaningAreaQhawaxDate(db.session,installation_id)
            content = 'Fecha de Ultima Limpiza: %s \n Qhawax listo para la limpieza' % (date)
        sendEmail(to=app.config['MAIL_DEFAULT_RECEIVER'], subject=subject, template=content)
        json_message = jsonify({'OK': 'Email sent for maintenance date: %s' % (comercial_name)})
        return make_response(json_message, RESPONSE_CODES['OK'])
    else:
        json_message = jsonify({'error': 'Qhawax not found with name: %s' % (comercial_name)})
        return make_response(json_message, RESPONSE_CODES['NOT_FOUND'])