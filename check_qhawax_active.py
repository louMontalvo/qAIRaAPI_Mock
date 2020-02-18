import requests
import dateutil.parser
import datetime
from passlib.hash import bcrypt
from config import SECRET_KEY
import json

ALLOWED_TIME_MINUTES = 5
#BASE_URL = 'http://54.159.70.183/'
BASE_URL = 'http://127.0.0.1:8888/'
GET_QHAWAX_ACTIVE = BASE_URL + 'api/get_all_active_qhawax/'
GET_QHAWAX_TIMESTAMP_URL = BASE_URL + 'api/get_time_processed_data_active_qhawax/'
CRITICAL_TELEMETRY_ALERT_URL = BASE_URL + 'api/qhawax_critical_processed_data_timestamp_alert/'

def isQhawaxLostActivity(qhawax_lost_activity_timestamp_str, now_timestamp):
    return (now_timestamp - qhawax_lost_timestamp).total_seconds()/60 >= ALLOWED_TIME_MINUTES
all_active_qhawax_response=requests.get(GET_QHAWAX_ACTIVE)
json_data = json.loads(all_active_qhawax_response.text)
for qhawax in json_data:
	response_time = requests.get(GET_QHAWAX_TIMESTAMP_URL, params={'qhawax_name': qhawax['name']})
	if(response_time.text!=""):
		qhawax_lost_timestamp = dateutil.parser.parse(response_time.text) - datetime.timedelta(hours=5)
		print(qhawax_lost_timestamp)
		if isQhawaxLostActivity(qhawax_lost_timestamp, datetime.datetime.now()):
			response = requests.post(CRITICAL_TELEMETRY_ALERT_URL, json={'qhawax_name' : qhawax['name'],'secret_key' : bcrypt.hash(SECRET_KEY)})
	else:
		print("No hay registros en el qhawax: " + qhawax['name'])

#Cambie bcrypt.encrypt(SECRET_KEY) por bcrypt.hash(SECRET_KEY) 
