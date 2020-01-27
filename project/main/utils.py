import datetime
import dateutil
import dateutil.parser
import time

from project.database.models import AirQualityMeasurement, GasSensor, ProcessedMeasurement, Qhawax
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

def storeProcessedDataInDB(session, data):
    qhawax_name = data.pop('ID', None)
    qhawax_id = session.query(Qhawax.id).filter_by(name=qhawax_name).first()[0]
    
    processed_measurement = ProcessedMeasurement(**data, qhawax_id=qhawax_id)
    session.add(processed_measurement)
    session.commit()

def storeAirQualityDataInDB(session, data):
    qhawax_name = data.pop('ID', None)
    qhawax_id = session.query(Qhawax.id).filter_by(name=qhawax_name).first()[0]
    
    air_quality_data = {'CO': data['CO'], 'H2S': data['H2S'], 'SO2': data['SO2'], 'NO2': data['NO2'],
                        'O3': data['O3'], 'PM25': data['PM25'], 'PM10': data['PM10'], 'lat': data['lat'],
                        'lon': data['lon'], 'alt': data['alt'], 'timestamp': data['timestamp']}

    air_quality_measurement = AirQualityMeasurement(**air_quality_data, qhawax_id=qhawax_id)
    session.add(air_quality_measurement)
    session.commit()

def queryDBRaw(session, qhawax_name, initial_timestamp, final_timestamp):
    qhawax_id = session.query(Qhawax.id).filter_by(name=qhawax_name).first()[0]
    if qhawax_id is None:
        return None

    sensors = (RawMeasurement.CO_OP1, RawMeasurement.CO_OP2, RawMeasurement.CO2, RawMeasurement.H2S_OP1, 
                RawMeasurement.H2S_OP2, RawMeasurement.NO_OP1, RawMeasurement.NO_OP2, RawMeasurement.NO2_OP1, 
                RawMeasurement.NO2_OP2, RawMeasurement.O3_OP1, RawMeasurement.O3_OP2, RawMeasurement.PM1, 
                RawMeasurement.PM25, RawMeasurement.PM10, RawMeasurement.SO2_OP1, RawMeasurement.SO2_OP2, 
                RawMeasurement.VOC_OP1, RawMeasurement.VOC_OP2, RawMeasurement.UV, RawMeasurement.UVA, 
                RawMeasurement.UVB, RawMeasurement.spl, RawMeasurement.humidity, RawMeasurement.pressure, 
                RawMeasurement.temperature, RawMeasurement.lat, RawMeasurement.lon, RawMeasurement.alt, 
                RawMeasurement.timestamp)
    
    return session.query(*sensors).filter(RawMeasurement.qhawax_id == qhawax_id). \
                                    filter(RawMeasurement.timestamp > initial_timestamp). \
                                    filter(RawMeasurement.timestamp < final_timestamp). \
                                    order_by(RawMeasurement.timestamp).all()

def queryDBRealTimeProcessed(session, qhawax_name):
    qhawax_id = session.query(Qhawax.id).filter_by(name=qhawax_name).first()[0]
    if qhawax_id is None:
        return None

    sensors = (ProcessedMeasurement.CO, ProcessedMeasurement.CO2, ProcessedMeasurement.H2S, ProcessedMeasurement.NO,
                ProcessedMeasurement.NO2, ProcessedMeasurement.O3, ProcessedMeasurement.PM1, ProcessedMeasurement.PM25,
                ProcessedMeasurement.PM10, ProcessedMeasurement.SO2, ProcessedMeasurement.VOC, ProcessedMeasurement.UV,
                ProcessedMeasurement.UVA, ProcessedMeasurement.UVB, ProcessedMeasurement.spl, ProcessedMeasurement.humidity,
                ProcessedMeasurement.pressure, ProcessedMeasurement.temperature, ProcessedMeasurement.lat,
                ProcessedMeasurement.lon, ProcessedMeasurement.alt, ProcessedMeasurement.timestamp)

    return session.query(*sensors).filter(ProcessedMeasurement.qhawax_id == qhawax_id). \
                                    order_by(desc(ProcessedMeasurement.timestamp)).limit(10).all()

def queryDBProcessed(session, qhawax_name, initial_timestamp, final_timestamp):
    qhawax_id = session.query(Qhawax.id).filter_by(name=qhawax_name).first()[0]
    if qhawax_id is None:
        return None

    sensors = (ProcessedMeasurement.CO, ProcessedMeasurement.CO2, ProcessedMeasurement.H2S, ProcessedMeasurement.NO,
                ProcessedMeasurement.NO2, ProcessedMeasurement.O3, ProcessedMeasurement.PM1, ProcessedMeasurement.PM25,
                ProcessedMeasurement.PM10, ProcessedMeasurement.SO2, ProcessedMeasurement.VOC, ProcessedMeasurement.UV,
                ProcessedMeasurement.UVA, ProcessedMeasurement.UVB, ProcessedMeasurement.spl, ProcessedMeasurement.humidity,
                ProcessedMeasurement.pressure, ProcessedMeasurement.temperature, ProcessedMeasurement.lat,
                ProcessedMeasurement.lon, ProcessedMeasurement.alt, ProcessedMeasurement.timestamp)

    return session.query(*sensors).filter(ProcessedMeasurement.qhawax_id == qhawax_id). \
                                    filter(ProcessedMeasurement.timestamp > initial_timestamp). \
                                    filter(ProcessedMeasurement.timestamp < final_timestamp). \
                                    order_by(ProcessedMeasurement.timestamp).limit(10).all()

def queryDBAirQuality(session, qhawax_name, initial_timestamp, final_timestamp):
    qhawax_id = session.query(Qhawax.id).filter_by(name=qhawax_name).first()[0]
    if qhawax_id is None:
        return None

    sensors = (AirQualityMeasurement.CO, AirQualityMeasurement.H2S, AirQualityMeasurement.NO2,
                AirQualityMeasurement.O3, AirQualityMeasurement.PM25, AirQualityMeasurement.PM10, 
                AirQualityMeasurement.SO2, AirQualityMeasurement.lat, AirQualityMeasurement.lon, 
                AirQualityMeasurement.alt, AirQualityMeasurement.timestamp)
    
    return session.query(*sensors).filter(AirQualityMeasurement.qhawax_id == qhawax_id). \
                                    filter(AirQualityMeasurement.timestamp >= initial_timestamp). \
                                    filter(AirQualityMeasurement.timestamp <= final_timestamp). \
                                    order_by(AirQualityMeasurement.timestamp).all()

def averageMeasurementsInHours(measurements, initial_timestamp, final_timestamp, interval_hours):
    initial_hour_utc = initial_timestamp.astimezone(tz=dateutil.tz.tzutc()).replace(tzinfo=None)
    final_hour_utc = final_timestamp.astimezone(tz=dateutil.tz.tzutc()).replace(tzinfo=None)
    initial_hour = initial_hour_utc.replace(minute=0, second=0, microsecond=0)
    final_hour = final_hour_utc.replace(minute=0, second=0, microsecond=0)

    current_hour = initial_hour
    ind = 0
    measurements_in_timestamp = []
    averaged_measurements = []
    while current_hour < final_hour:
        if ind > len(measurements) - 1:
            break
        
        timestamp = measurements[ind]['timestamp']
        if timestamp >= current_hour and timestamp <= current_hour + datetime.timedelta(hours=interval_hours):
            measurements_in_timestamp.append(measurements[ind])
            ind += 1
        else:
            if len(measurements_in_timestamp) != 0:
                averaged_measurement = averageMeasurements(measurements_in_timestamp)
                averaged_measurement['timestamp'] = current_hour
                averaged_measurements.append(averaged_measurement)
            measurements_in_timestamp = []
            current_hour += datetime.timedelta(hours=interval_hours)
    
    if len(measurements_in_timestamp) != 0:
        averaged_measurement = averageMeasurements(measurements_in_timestamp)
        averaged_measurement['timestamp'] = current_hour
        averaged_measurements.append(averaged_measurement)

    return averaged_measurements

def averageMeasurements(measurements):
    SKIP_KEYS = ['timestamp', 'lat', 'lon']

    average_measurement = {}

    for sensor_name in measurements[0]:
        if sensor_name in SKIP_KEYS:
            continue
        
        sensor_values = [measurement[sensor_name] for measurement in measurements]
        if all([value is None for value in sensor_values]):
            average_measurement[sensor_name] = None
        else:
            sensor_values_without_none = [value for value in sensor_values if value is not None]
            average_measurement[sensor_name] = sum(sensor_values_without_none)/len(sensor_values_without_none)

    average_measurement['timestamp'] = measurements[-1]['timestamp']
    average_measurement['lat'] = measurements[-1]['lat']
    average_measurement['lon'] = measurements[-1]['lon']

    return average_measurement

def getLocationFromProductID(session, qhawax_id):
    qhawax_location = session.query(Qhawax._location).filter_by(name=qhawax_id).first()
    if qhawax_location is None:
        return {'lat': -1, 'lon': -1}

    return qhawax_location[0]

def getOffsetsFromProductID(session, qhawax_id):
    print('Entre a getOffsetsFromProductID')
    print(qhawax_id)
    qhawax_id = session.query(Qhawax.id).filter_by(name=qhawax_id).one()[0]
    print(qhawax_id)
    attributes = (GasSensor.type, GasSensor.WE, GasSensor.AE, GasSensor.sensitivity)
    sensors = session.query(*attributes).filter_by(qhawax_id=qhawax_id).all()
    print(sensors)

    offsets = {}
    for sensor in sensors:
        sensor_dict = sensor._asdict()
        offsets[sensor_dict.pop('type')] = sensor_dict
    
    return offsets
    
def getControlledOffsetsFromProductID(session, qhawax_id):
    qhawax_id = session.query(Qhawax.id).filter_by(name=qhawax_id).one()[0]

    attributes = (GasSensor.type, GasSensor.C2, GasSensor.C1, GasSensor.C0)
    sensors = session.query(*attributes).filter_by(qhawax_id=qhawax_id).all()

    controlled_offsets = {}
    for sensor in sensors:
        sensor_dict = sensor._asdict()
        controlled_offsets[sensor_dict.pop('type')] = sensor_dict
    
    return controlled_offsets

def getNonControlledOffsetsFromProductID(session, qhawax_id):
    qhawax_id = session.query(Qhawax.id).filter_by(name=qhawax_id).one()[0]

    attributes = (GasSensor.type, GasSensor.NC1, GasSensor.NC0)
    sensors = session.query(*attributes).filter_by(qhawax_id=qhawax_id).all()

    non_controlled_offsets = {}
    for sensor in sensors:
        sensor_dict = sensor._asdict()
        non_controlled_offsets[sensor_dict.pop('type')] = sensor_dict
    
    return non_controlled_offsets

def getAllLocations(session):
    locations = []

    all_qhawax = session.query(Qhawax.name, Qhawax._location).all()

    for qhawax in all_qhawax:
        data = {'id': qhawax.name}
        data['location'] = qhawax._location
        locations.append(data)

    return locations

def saveLocationFromProductID(session, qhawax_id, lat, lon):
    new_location = Location(lat=lat, lon=lon)
    session.query(Qhawax).filter_by(name=qhawax_id).update(values={'_location': new_location.serialize})
    session.commit()

def saveOffsetsFromProductID(session, qhawax_id, offsets):
    qhawax_id = session.query(Qhawax.id).filter_by(name=qhawax_id).one()[0]

    for sensor_type in offsets:
        session.query(GasSensor).filter_by(qhawax_id=qhawax_id, type=sensor_type).update(values=offsets[sensor_type])

    session.commit()

def saveControlledOffsetsFromProductID(session, qhawax_id, controlled_offsets):
    qhawax_id = session.query(Qhawax.id).filter_by(name=qhawax_id).one()[0]

    for sensor_type in controlled_offsets:
        session.query(GasSensor).filter_by(qhawax_id=qhawax_id, type=sensor_type).update(values=controlled_offsets[sensor_type])
    
    session.commit()
    
def saveNonControlledOffsetsFromProductID(session, qhawax_id, non_controlled_offsets):
    qhawax_id = session.query(Qhawax.id).filter_by(name=qhawax_id).one()[0]

    for sensor_type in non_controlled_offsets:
        session.query(GasSensor).filter_by(qhawax_id=qhawax_id, type=sensor_type).update(values=non_controlled_offsets[sensor_type])
    
    session.commit()

def updateMainIncaInDB(session, new_main_inca, qhawax_name):
    session.query(Qhawax).filter_by(name=qhawax_name).update(values={'main_inca': new_main_inca})
    session.commit()

def queryDBlistaSensor(session, qhawax_name, sensor, initial_timestamp, final_timestamp):
    qhawax_id = session.query(Qhawax.id).filter_by(name=qhawax_name).first()[0]
    if qhawax_id is None:
        return None
    
    if sensor == 'CO':
        datos = AirQualityMeasurement.CO
    elif sensor == 'NO2':
        datos = AirQualityMeasurement.NO2
    elif sensor == 'PM10':
        datos = AirQualityMeasurement.PM10
    elif sensor == 'PM25':
        datos = AirQualityMeasurement.PM25
    elif sensor == 'SO2':
        datos = AirQualityMeasurement.SO2
        
    resultado = session.query(datos).filter(AirQualityMeasurement.qhawax_id == qhawax_id). \
                                 filter(AirQualityMeasurement.timestamp >= initial_timestamp). \
                                 filter(AirQualityMeasurement.timestamp <= final_timestamp). \
                                 order_by(AirQualityMeasurement.timestamp).all()
    
    if len(resultado) == 0:
        return 0
    else:
        return resultado

def queryDBPROM(session, qhawax_name, sensor, initial_timestamp, final_timestamp):
    qhawax_id = session.query(Qhawax.id).filter_by(name=qhawax_name).first()[0]
    if qhawax_id is None:
        return None
    
    if sensor == 'CO':
        datos = AirQualityMeasurement.CO
        hoursPerSensor = 8
    elif sensor == 'NO2':
        datos = AirQualityMeasurement.NO2
        hoursPerSensor = 1
    elif sensor == 'PM10':
        datos = AirQualityMeasurement.PM10
        hoursPerSensor = 24
    elif sensor == 'PM25':
        datos = AirQualityMeasurement.PM25
        hoursPerSensor = 24
    elif sensor == 'SO2':
        datos = AirQualityMeasurement.SO2
        hoursPerSensor = 24
    elif sensor == 'O3':
        datos = AirQualityMeasurement.O3
        hoursPerSensor = 8

    resultado=[]
    resultado = session.query(datos).filter(AirQualityMeasurement.qhawax_id == qhawax_id). \
                                      filter(AirQualityMeasurement.timestamp > initial_timestamp). \
                                      filter(AirQualityMeasurement.timestamp < final_timestamp). \
                                      order_by(AirQualityMeasurement.timestamp).all()


    sum = 0        

    if len(resultado) == 0 :
        return 0
    else :
        for i in range(len(resultado)):
            sum = sum + resultado[i][0]
        promf = sum /len(resultado)
        
        return promf

def queryIncaQhawax(session, name):
    qhawax_inca = session.query(Qhawax.main_inca).filter_by(name=name).one()
    if qhawax_inca == 50:
        resultado = 'green'
    elif qhawax_inca == 100:
        resultado = 'yellow'
    elif qhawax_inca == 500:
        resultado = 'orange'
    elif qhawax_inca == 600:
        resultado = 'red'
    else:
        resultado = 'green'
    return resultado