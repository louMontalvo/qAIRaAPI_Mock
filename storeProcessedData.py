import math
import requests
import datetime
import sys

#BASE_URL = 'http://54.159.70.183/'
BASE_URL = 'http://127.0.0.1:8888/'
ACTIVE_QHAWAX_ENDPOINT = 'api/get_all_active_qhawax/'
OFFSETS_ENDPOINT = 'api/request_offsets/'
CONTROLLED_OFFSETS_ENDPOINT = 'api/request_controlled_offsets/'
NON_CONTROLLED_OFFSETS_ENDPOINT = 'api/request_non_controlled_offsets/'
RAW_DATA_ENDPOINT = 'api/raw_measurements/'
PROCESSED_DATA_ENDPOINT = 'api/processed_measurements/'

TEMPERATURE_CORRECTIONS = {
    'NO': {
        -30: 2.90, -20: 2.90, -10: 2.20, 0: 1.80, 10: 1.70,
        20: 1.60, 30: 1.50, 40: 1.40, 50: 1.30
    },
    'NO2': {
        -30: 1.30, -20: 1.30, -10: 1.3, 0: 1.30, 10: 1.00,
        20: 0.6, 30: 0.4, 40: 0.2, 50: -1.50
    },
    'CO': {
        -30: 0.7, -20: 0.7, -10: 0.7, 0: 0.7, 10: 1.00,
        20: 3.00, 30: 3.50, 40: 4.00, 50: 4.50
    },
    'SO2': {
        -30: 1.60, -20: 1.60, -10: 1.60, 0: 1.60, 10: 1.60,
        20: 1.60, 30: 1.90, 40: 3.00, 50: 5.80
    },
    'H2S': {
        -30: -0.6, -20: -0.6, -10: 0.1, 0: 0.8, 10: -0.7,
        20: -2.50, 30: -2.50, 40: -2.20, 50: -1.80
    },
    'O3': {
        -30: 0.90, -20: 0.90, -10: 1.00, 0: 1.30, 10: 1.50,
        20: 1.70, 30: 2.00, 40: 2.50, 50: 3.70
    }
}

MIN_TEMPERATURE = -30
MAX_TEMPERATURE = 50

def averageProcessedMeasurements(processed_measurements):
    SKIP_KEYS = ['timestamp']
    average_processed_measurement = {}
    for sensor_name in processed_measurements[0]:
        if sensor_name in SKIP_KEYS:
            continue
        sensor_values = [measurement[sensor_name] for measurement in processed_measurements]
        if all([value is None for value in sensor_values]):
            average_processed_measurement[sensor_name] = None 
        else:
            sensor_values_without_none = [value for value in sensor_values if value is not None]
            if(len(sensor_values_without_none)>0):
                average_processed_measurement[sensor_name] = sum(sensor_values_without_none)/len(sensor_values_without_none)
    
    average_processed_measurement['timestamp'] = processed_measurements[-1]['timestamp']

    return average_processed_measurement

def sortSensors(op1_op2_measurements):
    #print(sorted(op1_op2_measurements.keys()))
    sort_dict={}
    o3_value = op1_op2_measurements['O3']
    del op1_op2_measurements['O3']
    for i in sorted(op1_op2_measurements.keys()):
        sort_dict[i]=op1_op2_measurements[i]
    op1_op2_measurements['O3']=o3_value
    return op1_op2_measurements



def processRawMeasurement(raw_measurement, sensor_offsets, controlled_offsets, non_controlled_offsets,CNO2):
    SKIP_KEYS = ['timestamp', 'lat', 'lon', 'alt']
    measurement = {key:value for key, value in raw_measurement.items() if value is not None}
    
    # Create object with OP1 OP2 measurement
    op1_op2_measurements = {}
    processed_measurement = {}
    for sensor_full_name in measurement:
        sensor_name, _, sensor_channel = sensor_full_name.partition('_')
        if sensor_channel == '':
            sensor_value = measurement[sensor_full_name]
            processed_measurement[sensor_name] = sensor_value
            if sensor_full_name not in SKIP_KEYS:
                processed_measurement[sensor_name] = round(sensor_value, 3)
        else:
            if sensor_name not in op1_op2_measurements:
                op1_op2_measurements[sensor_name] = {}
            op1_op2_measurements[sensor_name][sensor_channel] = measurement[sensor_full_name]

    op1_op2_measurements = sortSensors(op1_op2_measurements)

    for sensor_name in op1_op2_measurements:
        op1_op2_measurement = {
            'name': sensor_name,
            'OP1': op1_op2_measurements[sensor_name]['OP1'],
            'OP2': op1_op2_measurements[sensor_name]['OP2'],
            'temperature': measurement['temperature']
        }
        processed_sensor = processSensorChannels(op1_op2_measurement, sensor_offsets[sensor_name],CNO2)
        if(sensor_name == 'NO2'):
            CNO2 = processed_sensor*sensor_offsets[sensor_name]['sensitivity']
        processed_sensor = applyControlledCorrection(processed_sensor, controlled_offsets[sensor_name])
        processed_sensor = applyNonControlledCorrection(processed_sensor, non_controlled_offsets[sensor_name])
        processed_measurement[sensor_name] = round(processed_sensor, 3)

    return processed_measurement

def processSensorChannels(op1_op2_measurement, sensor_offsets,CNO2):
    temperature_correction = computeTemperatureCorrection(op1_op2_measurement['name'], op1_op2_measurement['temperature'])
    OP1_difference = op1_op2_measurement['OP1'] - sensor_offsets['WE'] - CNO2*sensor_offsets['sensitivity_2']
    OP2_difference = op1_op2_measurement['OP2'] - sensor_offsets['AE']
    result=0
    if(sensor_offsets['sensitivity']>0):
        result =(OP1_difference - OP2_difference*temperature_correction)/sensor_offsets['sensitivity']
    return result

def applyControlledCorrection(sensor_value, controlled_offsets):
    return controlled_offsets['C2'] * sensor_value * sensor_value + \
            controlled_offsets['C1'] * sensor_value + \
            controlled_offsets['C0']

def applyNonControlledCorrection(sensor_value, non_controlled_offsets):
    return non_controlled_offsets['NC1'] * sensor_value + non_controlled_offsets['NC0']

def computeTemperatureCorrection(sensor_name, temperature):
    if temperature < MIN_TEMPERATURE or temperature > MAX_TEMPERATURE or \
        sensor_name not in TEMPERATURE_CORRECTIONS:
        return 0
    
    corrections = TEMPERATURE_CORRECTIONS[sensor_name]
    if temperature in corrections:
        return corrections[temperature]
    
    lower_temp = math.floor(temperature/10)*10
    upper_temp = math.floor((temperature/10)+1)*10

    x0 = lower_temp
    x1 = upper_temp
    y0 = corrections[lower_temp]
    y1 = corrections[upper_temp]
    result=0
    if((x1 - x0)>0):
        result=y0 + (y1 - y0)*(temperature - x0)/(x1 - x0)
    return result

# Request all qhawax
response = requests.get(BASE_URL + ACTIVE_QHAWAX_ENDPOINT)
qhawax_names = [qhawax['name'] for qhawax in response.json()]
for qhawax_name in qhawax_names:
    print('Processing %s...' % (qhawax_name))
    # Request last minute data
    params = {'name': qhawax_name, 'interval_minutes': '1'}
    response = requests.get(BASE_URL + RAW_DATA_ENDPOINT, params=params)
    raw_measurements = response.json()

    if len(raw_measurements) == 0:
        continue

    # Request offsets
    params = {'ID': qhawax_name}
    response = requests.get(BASE_URL + OFFSETS_ENDPOINT, params=params)
    sensor_offsets = response.json()
    # Request controlled offsets
    params = {'ID': qhawax_name}
    response = requests.get(BASE_URL + CONTROLLED_OFFSETS_ENDPOINT, params=params)
    controlled_offsets = response.json()
    # Request non-controlled 
    params = {'ID': qhawax_name}
    response = requests.get(BASE_URL + NON_CONTROLLED_OFFSETS_ENDPOINT, params=params)
    non_controlled_offsets = response.json()
    processed_array=[]
    for measurement in raw_measurements:
        CNO2=0
        # Convert raw data to processed data
        processed_measurement = processRawMeasurement(measurement, sensor_offsets, controlled_offsets, non_controlled_offsets,CNO2)
        processed_array.append(processed_measurement)
    
    #Average measurements
    average_processed_measurement = averageProcessedMeasurements(processed_array)
    average_processed_measurement['ID'] = qhawax_name
    #print(average_processed_measurement)
    # Store processed data in db
    response = requests.post(BASE_URL + PROCESSED_DATA_ENDPOINT, json=processed_measurement)
    print(response.text)
