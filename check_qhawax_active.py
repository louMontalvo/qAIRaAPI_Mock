import requests
import dateutil.parser
import datetime
from passlib.hash import bcrypt
from config import SECRET_KEY
import json

ALLOWED_TIME_MINUTES = 30
#BASE_URL = 'http://54.159.70.183/'
BASE_URL = 'http://127.0.0.1:8888/'
GET_ALL_QHAWAX_NAME_URL = BASE_URL + 'api/get_all_qhawax/'
GET_QHAWAX_TIMESTAMP_URL = BASE_URL + 'api/qhawax_active/'
CRITICAL_TELEMETRY_ALERT_URL = BASE_URL + 'api/qhawax_critical_timestamp_alert/'
QHAWAX_STATUS_OFF = BASE_URL + 'api/qhawax_change_status_off/'
QHAWAX_STATUS_ON = BASE_URL + 'api/qhawax_change_status_on/'
GET_QHAWAX_STATUS = BASE_URL + 'api/qhawax_status/'

def isQhawaxLostActivity(qhawax_lost_activity_timestamp_str, now_timestamp):
    return (now_timestamp - qhawax_lost_timestamp).total_seconds()/60 >= ALLOWED_TIME_MINUTES

all_qhawax_name_response=requests.get(GET_ALL_QHAWAX_NAME_URL)
json_data = json.loads(all_qhawax_name_response.text)
for qhawax in json_data:
	print(qhawax)
	response_time = requests.get(GET_QHAWAX_TIMESTAMP_URL, params={'qhawax_name': qhawax['name']})
	if(response_time.text!=""):
		qhawax_lost_timestamp = dateutil.parser.parse(response_time.text)
		if isQhawaxLostActivity(qhawax_lost_timestamp, datetime.datetime.now()):
			print("Lost Activity")
			response_update = requests.post(QHAWAX_STATUS_OFF,json={'qhawax_name' : qhawax['name']})
			response = requests.post(CRITICAL_TELEMETRY_ALERT_URL, json={'qhawax_name' : qhawax['name'],'secret_key' : bcrypt.hash(SECRET_KEY)})
		else:
			print("Qhawax Running")
			if(requests.get(GET_QHAWAX_STATUS, params={'qhawax_name': qhawax['name']})!='ON'):
				response_update = requests.post(QHAWAX_STATUS_ON,json={'qhawax_name' : qhawax['name']})
	else:
		print("No hay registros en el qhawax: " + qhawax['name'])




#Cambie bcrypt.encrypt(SECRET_KEY) por bcrypt.hash(SECRET_KEY) 
