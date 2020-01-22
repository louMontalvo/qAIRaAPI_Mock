import datetime
import dateutil
import dateutil.parser
import time

from project.database.models import AirQualityMeasurement, GasSensor, ProcessedMeasurement, \
                                    Qhawax, RawMeasurement
from project.database.utils import Location

elapsed_time = None
data_storage = []
qhawax_storage = {}
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
MAX_SECONDS_DATA_STORAGE = 30
MAX_LEN_DATA_STORAGE = 30


def handleTimestampInData(data):
    if 'timestamp' not in data:
        data['timestamp'] = datetime.datetime.now()
    else:
        data['timestamp'] = dateutil.parser.parse(data['timestamp'])
    return data

def storeRawDataInDB(session, data):
    global elapsed_time, data_storage, qhawax_storage
    if elapsed_time is None:
        elapsed_time = time.time()
    
    if time.time() - elapsed_time >= MAX_SECONDS_DATA_STORAGE or len(data_storage) >= MAX_LEN_DATA_STORAGE:
        for raw_measurement in data_storage:
            session.add(raw_measurement)
        session.commit()

        data_storage = []
        elapsed_time = time.time()
    
    qhawax_name = data.pop('ID', None)
    if qhawax_name not in qhawax_storage:
        qhawax_id = session.query(Qhawax.id).filter_by(name=qhawax_name).first()
        qhawax_storage[qhawax_name] = qhawax_id[0]
    
    raw_measurement = RawMeasurement(**data, qhawax_id=qhawax_storage[qhawax_name])

    data_storage.append(raw_measurement)