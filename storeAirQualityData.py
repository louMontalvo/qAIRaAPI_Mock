import requests
import datetime

#BASE_URL = 'http://54.159.70.183/'
BASE_URL = 'http://127.0.0.1:8888/'
ACTIVE_QHAWAX_ENDPOINT = 'api/get_active_qhawax/'
PROCESSED_DATA_ENDPOINT = 'api/processed_measurements/'
AIR_QUALITY_DATA_ENDPOINT = 'api/air_quality_measurements/'

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
            averaged_value = sum(sensor_values_without_none)/len(sensor_values_without_none)
            if sensor_name not in ['lat', 'lon']:
                average_processed_measurement[sensor_name] = round(averaged_value, 3)
            else:
                average_processed_measurement[sensor_name] = averaged_value
    
    starting_hour = datetime.datetime.now() - datetime.timedelta(hours=1)
    average_processed_measurement['timestamp'] = str(starting_hour.replace(minute=0, second=0, microsecond=0))

    return average_processed_measurement

# Request all qhawax
response = requests.get(BASE_URL + ACTIVE_QHAWAX_ENDPOINT)
qhawax_names = [qhawax['name'] for qhawax in response.json()]

for qhawax_name in qhawax_names:
    print('Processing %s...' % (qhawax_name))
    params = {'name': qhawax_name, 'interval_hours': '1'}
    response = requests.get(BASE_URL + PROCESSED_DATA_ENDPOINT, params=params)
    processed_measurements = response.json()
    if len(processed_measurements) == 0:
        continue
    # Average measurements
    average_processed_measurement = averageProcessedMeasurements(processed_measurements)
    average_processed_measurement['ID'] = qhawax_name
    # Store averaged processed data in db
    response = requests.post(BASE_URL + AIR_QUALITY_DATA_ENDPOINT, json=average_processed_measurement)
    print(response.text)


