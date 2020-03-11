import datetime
import dateutil
import dateutil.parser
import time

from project.database.models import AirQualityMeasurement, GasSensor, ProcessedMeasurement, Qhawax, RawMeasurement, EcaNoise, GasInca, QhawaxInstallationHistory, Company, ValidProcessedMeasurement
from project.database.utils import Location

elapsed_time = None
data_storage = []
qhawax_storage = {}
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
MAX_SECONDS_DATA_STORAGE = 30
MAX_LEN_DATA_STORAGE = 30

#$
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

def getNoiseData(session,qhawax_name):
    eca_noise_id = session.query(Qhawax.eca_noise_id).filter_by(name=qhawax_name).first()
    zone = session.query(EcaNoise.area_name).filter_by(id=eca_noise_id).first()[0]
    return zone

def getQhawaxId(session, qhawax_name):
    qhawax_id = session.query(Qhawax.id).filter_by(name=qhawax_name).first()[0]
    return qhawax_id

def storeProcessedDataInDB(session, data):
    qhawax_name = data.pop('ID', None)
    qhawax_id = session.query(Qhawax.id).filter_by(name=qhawax_name).first()[0]
    data['PM1'] = data['PM1']/3
    data['PM25'] = data['PM25']/3
    data['PM10'] = data['PM10']/3
    if(qhawax_id==7 or qhawax_id==8):
       data['spl'] = (data['spl']-10)*10
    processed_measurement = ProcessedMeasurement(**data, qhawax_id=qhawax_id)
    session.add(processed_measurement)
    session.commit()

def storeValidProcessedDataInDB(session, data, qhawax_id):
    installation_id = session.query(QhawaxInstallationHistory.id).filter_by(qhawax_id=qhawax_id). \
                                    filter(QhawaxInstallationHistory.end_date == None). \
                                    order_by(QhawaxInstallationHistory.instalation_date.desc()).first()[0]
    data['PM1'] = data['PM1']/3
    data['PM25'] = data['PM25']/3
    data['PM10'] = data['PM10']/3
    if(qhawax_id==7 or qhawax_id==8):
       data['spl'] = (data['spl']-10)*10
    valid_data = {'timestamp': data['timestamp'],'CO': data['CO'], 'H2S': data['H2S'],'SO2': data['SO2'],
                'NO2': data['NO2'],'O3': data['O3'],'PM25': data['PM25'], 'VOC': data['VOC'],
                'PM1': data['PM1'],'PM10': data['PM10'],'UV': data['UV'],'UVA': data['UVA'],'UVB': data['UVB'],
                'SPL': data['spl'],'humidity': data['humidity'],'pressure': data['pressure'],'temperature': data['temperature'],
                'lat':data['lat'],'lon':data['lon']}
    valid_processed_measurement = ValidProcessedMeasurement(**valid_data, qhawax_installation_id=installation_id)
    session.add(valid_processed_measurement)
    session.commit()

def storeGasIncaInDB(session, data):
    qhawax_name = data.pop('ID', None)
    qhawax_id = session.query(Qhawax.id).filter_by(name=qhawax_name).first()[0]
    
    gas_inca_data = {'CO': data['CO'], 'H2S': data['H2S'], 'SO2': data['SO2'], 'NO2': data['NO2'],'O3': data['O3'],
             'PM25': data['PM25'], 'PM10': data['PM10'],'timestamp': data['timestamp'],'main_inca':data['main_inca']}
    gas_inca_processed = GasInca(**gas_inca_data, qhawax_id=qhawax_id)
    session.add(gas_inca_processed)
    session.commit()

#$ esto es del script
def storeAirQualityDataInDB(session, data):
    qhawax_name = data.pop('ID', None)
    qhawax_id = session.query(Qhawax.id).filter_by(name=qhawax_name).first()[0]
    
    air_quality_data = {'CO': data['CO'], 'H2S': data['H2S'], 'SO2': data['SO2'], 'NO2': data['NO2'],
                        'O3': data['O3'], 'PM25': data['PM25'], 'PM10': data['PM10'], 'lat': data['lat'],
                        'lon': data['lon'], 'alt': data['alt'], 'timestamp': data['timestamp']}

    air_quality_measurement = AirQualityMeasurement(**air_quality_data, qhawax_id=qhawax_id)
    session.add(air_quality_measurement)
    session.commit()

#$
def queryDBNextProcessedMeasurement(session, qhawax_name, lastID):
    qhawax_id = session.query(Qhawax.id).filter_by(name=qhawax_name).first()[0]
    if qhawax_id is None:
        return None

    sensors = (ProcessedMeasurement.id, ProcessedMeasurement.CO, ProcessedMeasurement.CO2, ProcessedMeasurement.H2S, ProcessedMeasurement.NO,
                ProcessedMeasurement.NO2, ProcessedMeasurement.O3, ProcessedMeasurement.PM1, ProcessedMeasurement.PM25,
                ProcessedMeasurement.PM10, ProcessedMeasurement.SO2, ProcessedMeasurement.VOC, ProcessedMeasurement.UV,
                ProcessedMeasurement.UVA, ProcessedMeasurement.UVB, ProcessedMeasurement.spl, ProcessedMeasurement.humidity,
                ProcessedMeasurement.pressure, ProcessedMeasurement.temperature, ProcessedMeasurement.lat,
                ProcessedMeasurement.lon, ProcessedMeasurement.alt, ProcessedMeasurement.timestamp)

    return session.query(*sensors).filter(ProcessedMeasurement.qhawax_id == qhawax_id). \
                                   filter(ProcessedMeasurement.id > lastID). \
                                   order_by(ProcessedMeasurement.timestamp.desc()).limit(10000).all()

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

#$
def queryDBRealTimeProcessed(session, qhawax_name):
    qhawax_id = session.query(Qhawax.id).filter_by(name=qhawax_name).first()[0]
    if qhawax_id is None:
        return None

    sensors = (ProcessedMeasurement.id, ProcessedMeasurement.CO, ProcessedMeasurement.CO2, ProcessedMeasurement.H2S, ProcessedMeasurement.NO,
                ProcessedMeasurement.NO2, ProcessedMeasurement.O3, ProcessedMeasurement.PM1, ProcessedMeasurement.PM25,
                ProcessedMeasurement.PM10, ProcessedMeasurement.SO2, ProcessedMeasurement.VOC, ProcessedMeasurement.UV,
                ProcessedMeasurement.UVA, ProcessedMeasurement.UVB, ProcessedMeasurement.spl, ProcessedMeasurement.humidity,
                ProcessedMeasurement.pressure, ProcessedMeasurement.temperature, ProcessedMeasurement.lat,
                ProcessedMeasurement.lon, ProcessedMeasurement.alt, ProcessedMeasurement.timestamp)

    return session.query(*sensors).order_by(ProcessedMeasurement.timestamp.desc()).limit(10000).all()

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
                                    order_by(ProcessedMeasurement.timestamp).all()

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


def queryDBGasInca(session,initial_timestamp, final_timestamp):
    sensors = (GasInca.CO, GasInca.H2S, GasInca.SO2, GasInca.NO2,GasInca.O3, 
                GasInca.PM25, GasInca.PM10, GasInca.SO2,GasInca.timestamp, GasInca.qhawax_id, GasInca.main_inca)
    
    return session.query(*sensors).filter(GasInca.timestamp >= initial_timestamp). \
                                    filter(GasInca.timestamp <= final_timestamp).all()

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
    qhawax_id = session.query(Qhawax.id).filter_by(name=qhawax_id).one()[0]
    attributes = (GasSensor.type, GasSensor.WE, GasSensor.AE, GasSensor.sensitivity, GasSensor.sensitivity_2)
    sensors = session.query(*attributes).filter_by(qhawax_id=qhawax_id).all()
    all_sensors=['CO','SO2','H2S','O3','NO','NO2']

    initial_offsets = {}
    for sensor in all_sensors:
        initial_offsets[sensor] = {'WE': 0.0, 'AE': 0.0, 'sensitivity': 0.0, 'sensitivity_2': 0.0}

    for sensor in sensors:
        sensor_dict = sensor._asdict()
        initial_offsets[sensor_dict.pop('type')] = sensor_dict

    return initial_offsets
    
def getControlledOffsetsFromProductID(session, qhawax_id):
    qhawax_id = session.query(Qhawax.id).filter_by(name=qhawax_id).one()[0]
    attributes = (GasSensor.type, GasSensor.C2, GasSensor.C1, GasSensor.C0)
    sensors = session.query(*attributes).filter_by(qhawax_id=qhawax_id).all()
    all_sensors=['CO','SO2','H2S','O3','NO','NO2']

    initial_offsets = {}
    for sensor in all_sensors:
        initial_offsets[sensor] = {'C0': 0.0, 'C1': 0.0, 'C2': 0.0}

    for sensor in sensors:
        sensor_dict = sensor._asdict()
        initial_offsets[sensor_dict.pop('type')] = sensor_dict
    
    return initial_offsets

def getNonControlledOffsetsFromProductID(session, qhawax_id):
    qhawax_id = session.query(Qhawax.id).filter_by(name=qhawax_id).one()[0]

    attributes = (GasSensor.type, GasSensor.NC1, GasSensor.NC0)
    sensors = session.query(*attributes).filter_by(qhawax_id=qhawax_id).all()
    all_sensors=['CO','SO2','H2S','O3','NO','NO2']

    initial_offsets = {}
    for sensor in all_sensors:
        initial_offsets[sensor] = {'NC1': 0.0, 'NC0': 0.0}

    for sensor in sensors:
        sensor_dict = sensor._asdict()
        initial_offsets[sensor_dict.pop('type')] = sensor_dict
    return initial_offsets

def getAllLocations(session):
    locations = []

    all_qhawax = session.query(Qhawax.name, Qhawax._location).all()

    for qhawax in all_qhawax:
        data = {'id': qhawax.name}
        data['location'] = qhawax._location
        locations.append(data)

    return locations

def getQhawaxStatus(session, qhawax_id):
    state = session.query(Qhawax.state).filter_by(name=qhawax_id).one()[0]
    return state

def saveStatusOff(session, qhawax_id):
    session.query(Qhawax).filter_by(name=qhawax_id).update(values={'state': "OFF",'main_inca':None})
    session.commit()

def saveStatusOn(session, qhawax_id):
    main_inca= session.query(GasInca.main_inca).filter_by(qhawax_id=qhawax_id).\
                                                    order_by(GasInca.id.desc()).first()[0]
    session.query(Qhawax).filter_by(name=qhawax_id).update(values={'state': "ON",'main_inca':main_inca})
    session.commit()

def saveTurnOnLastTime(session, qhawax_name):
    qhawax_id = session.query(Qhawax.id).filter_by(name=qhawax_name).first()
    installation_id = session.query(QhawaxInstallationHistory.id).filter_by(qhawax_id=qhawax_id).\
                             filter(QhawaxInstallationHistory.end_date == None). \
                             order_by(QhawaxInstallationHistory.instalation_date.desc()).first()[0]
    now = datetime.datetime.now()-datetime.timedelta(hours=5)
    session.query(QhawaxInstallationHistory).filter_by(id=installation_id).update(values={'last_time_physically_turn_on': now.replace(tzinfo=None)})
    session.commit()

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

def saveLocationFromProductID(session, qhawax_id, lat, lon):
    new_location = Location(lat=lat, lon=lon)
    session.query(Qhawax).filter_by(name=qhawax_id).update(values={'_location': new_location.serialize})
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
    elif sensor == 'H2S':
        datos = AirQualityMeasurement.H2S
        hoursPerSensor = 24

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
    if qhawax_inca[0] == 50:
        resultado = 'green'
    elif qhawax_inca[0] == 100:
        resultado = 'yellow'
    elif qhawax_inca[0] == 500:
        resultado = 'orange'
    elif qhawax_inca[0] == 600:
        resultado = 'red'
    else:
        resultado = 'green'
    return resultado

def getQhawaxLatestTimestamp(session, qhawax_name):
    qhawax_id = session.query(Qhawax.id).filter_by(name=qhawax_name).one().id
    qhawax_time = session.query(RawMeasurement.timestamp).filter_by(qhawax_id=qhawax_id).first()
    raw_measurement_timestamp=""
    if(qhawax_time!=None):
        raw_measurement_timestamp = session.query(RawMeasurement.timestamp).filter_by(qhawax_id=qhawax_id) \
            .order_by(RawMeasurement.id.desc()).first().timestamp
    return raw_measurement_timestamp

def getQhawaxLatestTimestampProcessedMeasurement(session, qhawax_name):
    qhawax_id = session.query(Qhawax.id).filter_by(name=qhawax_name).one().id
    qhawax_time = session.query(ProcessedMeasurement.timestamp).filter_by(qhawax_id=qhawax_id).first()
    processed_measurement_timestamp=""
    if(qhawax_time!=None):
        processed_measurement_timestamp = session.query(ProcessedMeasurement.timestamp).filter_by(qhawax_id=qhawax_id) \
            .order_by(ProcessedMeasurement.id.desc()).first().timestamp
    return processed_measurement_timestamp

def getQhawaxLatestCoordinatesFromName(session, qhawax_name):
    return session.query(Qhawax._location).filter_by(name=qhawax_name).first()

def queryGetEcaNoise(session, eca_noise_id):
    fields = (EcaNoise.id, EcaNoise.area_name, EcaNoise.max_daytime_limit, EcaNoise.max_night_limit)
    return session.query(*fields).filter(EcaNoise.id == eca_noise_id).one()

#$
def queryDBGasAverageMeasurement(session, qhawax_name, gas_name):
    qhawax_id = session.query(Qhawax.id).filter_by(name=qhawax_name).first()[0]
    if qhawax_id is None:
        return None

    initial_timestamp = datetime.datetime.now() - datetime.timedelta(hours=5)
    last_timestamp = datetime.datetime.now() - datetime.timedelta(hours=29)

    if(gas_name=='CO'):
        sensors = (AirQualityMeasurement.timestamp, AirQualityMeasurement.CO.label('sensor'))
    elif(gas_name=='H2S'):
        sensors = (AirQualityMeasurement.timestamp, AirQualityMeasurement.H2S.label('sensor'))
    elif(gas_name=='NO2'):
        sensors = (AirQualityMeasurement.timestamp, AirQualityMeasurement.NO2.label('sensor'))
    elif(gas_name=='O3'):
        sensors = (AirQualityMeasurement.timestamp, AirQualityMeasurement.O3.label('sensor'))
    elif(gas_name=='PM25'):
        sensors = (AirQualityMeasurement.timestamp, AirQualityMeasurement.PM25.label('sensor'))
    elif(gas_name=='PM10'):
        sensors = (AirQualityMeasurement.timestamp, AirQualityMeasurement.PM10.label('sensor'))
    elif(gas_name=='SO2'):
        sensors = (AirQualityMeasurement.timestamp, AirQualityMeasurement.SO2.label('sensor'))

    return session.query(*sensors).filter(AirQualityMeasurement.qhawax_id == qhawax_id). \
                               filter(AirQualityMeasurement.timestamp >= last_timestamp). \
                               filter(AirQualityMeasurement.timestamp <= initial_timestamp). \
                               order_by(AirQualityMeasurement.id.desc()).all()

def storeNewQhawaxInstallation(session, data):
    installation_data = {'lat': data['lat'], 'lon': data['lon'], 'instalation_date': data['instalation_date'], 'link_report': data['link_report'], 
             'observations': data['observations'], 'district': data['district'],'comercial_name': data['comercial_name'],'address':data['address'],
             'company_id': data['company_id'],'eca_noise_id':data['eca_noise_id'], 'qhawax_id':data['qhawax_id'],'connection_type':data['connection_type'],
             'index_type':data['index_type'],'measuring_height':data['measuring_height'], 'season':data['season'] }
    qhawax_installation = QhawaxInstallationHistory(**installation_data)
    session.add(qhawax_installation)
    session.commit()

def setOccupiedQhawax(session,qhawax_id):
    session.query(Qhawax).filter_by(id=qhawax_id).update(values={'availability': 'Occupied'})
    session.commit()
 
def setAvailableQhawax(session,qhawax_id):
    session.query(Qhawax).filter_by(id=qhawax_id).update(values={'availability': 'Available'})
    session.commit()

def saveEndWorkFieldDate(session, installation_id,end_date):
    session.query(QhawaxInstallationHistory).filter_by(id=installation_id).update(values={'end_date': end_date})
    session.commit()

def queryQhawaxInField(session):
    sensors = (QhawaxInstallationHistory.id, QhawaxInstallationHistory.qhawax_id, 
             QhawaxInstallationHistory.comercial_name, QhawaxInstallationHistory.company_id,QhawaxInstallationHistory.instalation_date)

    return session.query(*sensors).filter(QhawaxInstallationHistory.end_date == None). \
                                    order_by(QhawaxInstallationHistory.instalation_date.desc()).all()

def getCompanyName(session, qhawax_in_field_list):
    for installation in qhawax_in_field_list:
        company_name= session.query(Company.name).filter_by(id=installation['company_id']).first()[0]
        installation['company_name'] = company_name
    return qhawax_in_field_list

def queryQhawaxInFieldByCompany(session,company_id):
    sensors = (QhawaxInstallationHistory.qhawax_id, QhawaxInstallationHistory.comercial_name, 
                    QhawaxInstallationHistory.lat, QhawaxInstallationHistory.lon, QhawaxInstallationHistory.eca_noise_id)
    if(int(company_id) == 1):
        return session.query(*sensors).filter(QhawaxInstallationHistory.end_date == None).all()  
    return session.query(*sensors).filter(QhawaxInstallationHistory.company_id == company_id). \
                                       filter(QhawaxInstallationHistory.end_date == None).all()

def getQhawaxDetail(session, qhawax_in_field_by_company_list):
    for qhawax_detail in qhawax_in_field_by_company_list:
        qhawax_detail['qhawax_state']= session.query(Qhawax.state).filter_by(id=qhawax_detail['qhawax_id']).first()[0]
        qhawax_detail['qhawax_type'] = session.query(Qhawax.qhawax_type).filter_by(id=qhawax_detail['qhawax_id']).first()[0]
        qhawax_detail['qhawax_name'] = session.query(Qhawax.name).filter_by(id=qhawax_detail['qhawax_id']).first()[0]
        if(qhawax_detail['qhawax_state']=='OFF'):
            qhawax_detail['main_inca']   = session.query(Qhawax.main_inca).filter_by(id=qhawax_detail['qhawax_id']).first()[0]
        else:
            qhawax_detail['main_inca']   = session.query(GasInca.main_inca).filter_by(qhawax_id=qhawax_detail['qhawax_id']).\
                                                    order_by(GasInca.id.desc()).first()[0]
    return qhawax_in_field_by_company_list

def getAvailableQhawax(session):
    available_qhawax = db.session.query(Qhawax.id, Qhawax.name, Qhawax.qhawax_type, Qhawax.state).filter_by(availability='Available').all()
    return available_qhawax

def queryQhawaxRecord(session, qhawax_id):
    sensors = (QhawaxInstallationHistory.id, QhawaxInstallationHistory.comercial_name, 
               QhawaxInstallationHistory.lat, QhawaxInstallationHistory.lon,
               QhawaxInstallationHistory.address, QhawaxInstallationHistory.district,
               QhawaxInstallationHistory.instalation_date, QhawaxInstallationHistory.end_date)
    return session.query(*sensors).filter(QhawaxInstallationHistory.qhawax_id == qhawax_id). \
                                   order_by(QhawaxInstallationHistory.id.desc()).all()

def queryGetAreas(session):
    sensors = (EcaNoise.id, EcaNoise.area_name)
    return session.query(*sensors).order_by(EcaNoise.id.desc()).all()

def queryGetCompanies(session):
    sensors = (Company.id, Company.name)
    return session.query(*sensors).order_by(Company.id.desc()).all()

def queryQhawaxInstallationDetail(session, installation_id):
    sensors = (QhawaxInstallationHistory.id, QhawaxInstallationHistory.comercial_name, 
               QhawaxInstallationHistory.lat, QhawaxInstallationHistory.lon,
               QhawaxInstallationHistory.address, QhawaxInstallationHistory.district,
               QhawaxInstallationHistory.instalation_date, QhawaxInstallationHistory.end_date,
               QhawaxInstallationHistory.link_report,QhawaxInstallationHistory.qhawax_id,
               QhawaxInstallationHistory.connection_type, QhawaxInstallationHistory.index_type, 
               QhawaxInstallationHistory.measuring_height, QhawaxInstallationHistory.season,
               QhawaxInstallationHistory.last_maintenance_date, QhawaxInstallationHistory.last_cleaning_area_date ,
               QhawaxInstallationHistory.last_cleaning_equipment_date)
    return session.query(*sensors).filter(QhawaxInstallationHistory.id == installation_id).all()

def queryDateOfActiveQhawax(session):
    sensors = (QhawaxInstallationHistory.id,QhawaxInstallationHistory.instalation_date, QhawaxInstallationHistory.end_date,
               QhawaxInstallationHistory.last_maintenance_date, QhawaxInstallationHistory.last_cleaning_area_date ,
               QhawaxInstallationHistory.last_cleaning_equipment_date,QhawaxInstallationHistory.qhawax_id,
               QhawaxInstallationHistory.comercial_name)
    return session.query(*sensors).filter(QhawaxInstallationHistory.end_date == None).all()

def getCleaningEquipmentQhawaxDate(session, installation_id):
    return session.query(QhawaxInstallationHistory.last_cleaning_equipment_date).filter(QhawaxInstallationHistory.id == installation_id).first()[0]

def getCleaningAreaQhawaxDate(session, installation_id):
    return session.query(QhawaxInstallationHistory.last_cleaning_area_date).filter(QhawaxInstallationHistory.id == installation_id).first()[0]

def getMaintenanceQhawaxDate(session, installation_id):
    return session.query(QhawaxInstallationHistory.last_maintenance_date).filter(QhawaxInstallationHistory.id == installation_id).first()[0]

def getInstallationQhawaxDate(session, installation_id):
    return session.query(QhawaxInstallationHistory.instalation_date).filter(QhawaxInstallationHistory.id == installation_id).first()[0]

def getLastTurnOnTimeQhawax(session, qhawax_id):
    return session.query(QhawaxInstallationHistory.last_time_physically_turn_on).filter(QhawaxInstallationHistory.qhawax_id == qhawax_id).first()[0]
    
