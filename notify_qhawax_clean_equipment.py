import requests
import dateutil.parser
import datetime
from passlib.hash import bcrypt
from config import SECRET_KEY
import json

ALLOWED_TIME_HOURS = 24
#BASE_URL = 'http://54.159.70.183/'
BASE_URL = 'http://127.0.0.1:8888/'
GET_INSTALLED_ACTIVE_QHAWAX = BASE_URL + 'api/DatesofActiveQhawax/'
NOTIFY_MAINTENANCE_URL = BASE_URL + 'api/qhawax_notify_qhawax_cleaning_equipment/'

def isQhawaReadyToMaintenance(qhawax_date_str, now_timestamp):
    return (qhawax_date_str.replace(tzinfo=None)  - now_timestamp.replace(tzinfo=None) ).total_seconds()/3600 <= ALLOWED_TIME_HOURS

installed_active_qhawax_response=requests.get(GET_INSTALLED_ACTIVE_QHAWAX)
json_data = json.loads(installed_active_qhawax_response.text)
type_date =''
qhawax_last_timestamp=''
for qhawax_installed in json_data:
	if(qhawax_installed['last_cleaning_area_date']==None):
		type_date = 'Instalacion'
		qhawax_last_timestamp= dateutil.parser.parse(qhawax_installed['instalation_date'])
	else:
		type_date = 'Equipo'
		qhawax_last_timestamp = dateutil.parser.parse(qhawax_installed['last_cleaning_equipment_date'])
	if isQhawaReadyToMaintenance(qhawax_last_timestamp+datetime.timedelta(1*360/12), datetime.datetime.now()-datetime.timedelta(hours=5)):
		response = requests.post(NOTIFY_MAINTENANCE_URL, 
			json={'installation_id':qhawax_installed['id'],'comercial_name':qhawax_installed['comercial_name'],'type_date':type_date,'secret_key': bcrypt.hash(SECRET_KEY)})

#Cambie bcrypt.encrypt(SECRET_KEY) por bcrypt.hash(SECRET_KEY)
#Notificar cada mes
