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



@app.route('/api/get_eca_noise_limit/', methods=['GET'])
def getEcaNoiseLimitById():
    noiseID = request.args.get('ID')
    ecaNoiseInfo = utils.queryGetEcaNoise(db.session,noiseID)
    if ecaNoiseInfo is not None:
        return make_response(jsonify(ecaNoiseInfo), 200)
    return make_response(jsonify('Eca noise not found'), 404)


@app.route('/api/get_all_areas/', methods=['GET'])
def getAllAreas():
	allAreas = utils.queryGetAreas(db.session)
	if allAreas is not None:
		allAreas_list = [
        {'area_name': area.area_name,
        'id': area.id} for area in allAreas]
		return make_response(jsonify(allAreas_list), 200)
	return make_response(jsonify('Areas not found'), 404)


