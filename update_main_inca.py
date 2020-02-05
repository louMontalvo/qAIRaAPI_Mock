import requests
import math
import datetime
from passlib.hash import bcrypt


#BASE_URL = 'http://54.159.70.183/'
BASE_URL = 'http://127.0.0.1:8888/'
MAININCA_DATA_ENDPOINT = 'api/save_main_inca/'
GET_MEASUREMENT_PROM = 'api/measurementPromedio/'
ACTIVE_QHAWAX_ENDPOINT = 'api/get_all_active_qhawax/'

def validaH2S(val):
    calificacionInca = 0
    if val >=0 and val<= 50 :
        calificacionInca = 50
    elif val >50 and val<=100:
        calificacionInca = 100
    elif val >100 and val<=1000:
        calificacionInca = 500
    elif val >1000:
        calificacionInca = 600
    else:
        calificacionInca = -1

    return calificacionInca

def validaCO_NO2(val):
    calificacionInca = 0
    if val >=0 and val<= 50 :
        calificacionInca = 50
    elif val >50 and val<=100:
        calificacionInca = 100
    elif val >100 and val<=150:
        calificacionInca = 500
    elif val >150:
        calificacionInca = 600
    else:
        calificacionInca = -1

    return calificacionInca

def validaSO2(val):
    calificacionInca = 0
    if val >=0 and val<= 50 :
        calificacionInca = 50
    elif val >50 and val<=100:
        calificacionInca = 100
    elif val >100 and val<=625:
        calificacionInca = 500
    elif val >625:
        calificacionInca = 600
    else:
        calificacionInca = -1

    return calificacionInca

def validaPM10(val):
    calificacionInca = 0
    if val >=0 and val<= 50 :
        calificacionInca = 50
    elif val >50 and val<=100:
        calificacionInca = 100
    elif val >100 and val<=167:
        calificacionInca = 500
    elif val >167:
        calificacionInca = 600
    else:
        calificacionInca = -1

    return calificacionInca

def validaPM25(val):
    calificacionInca = 0
    if val >=0 and val<= 50 :
        calificacionInca = 50
    elif val >50 and val<=100:
        calificacionInca = 100
    elif val >100 and val<=500:
        calificacionInca = 500
    elif val >500:
        calificacionInca = 600
    else:
        calificacionInca = -1

    return calificacionInca

def validaO3(val):
    calificacionInca = 0
    if val >=0 and val<= 50 :
        calificacionInca = 50
    elif val >50 and val<=100:
        calificacionInca = 100
    elif val >100 and val<=175:
        calificacionInca = 500
    elif val >175:
        calificacionInca = 600
    else:
        calificacionInca = -1

    return calificacionInca

factor_final_CO = (0.0409 * 28.01 * 100)/10000
factor_final_NO2 = (0.0409 * 46.0055 * 100)/200
factor_final_PM10 = 100/150
factor_final_PM25 = 100/25
factor_final_SO2 = (0.0409 * 64.066 * 100)/20
factor_final_O3 = (0.0409 * 48* 100)/120
factor_final_H2S = (0.0409 * 34.1*100)/150

# Request all qhawax
response = requests.get(BASE_URL + ACTIVE_QHAWAX_ENDPOINT)
qhawax_names = [qhawax['name'] for qhawax in response.json()]
for qhawax_name in qhawax_names:
    try:
        responseCO = requests.get(BASE_URL + GET_MEASUREMENT_PROM, params={'name': qhawax_name, 'sensor': 'CO', 'hoursSensor': 8})
        responseNO2 = requests.get(BASE_URL + GET_MEASUREMENT_PROM, params={'name': qhawax_name, 'sensor': 'NO2', 'hoursSensor': 1})
        responsePM10 = requests.get(BASE_URL + GET_MEASUREMENT_PROM, params={'name': qhawax_name, 'sensor': 'PM10', 'hoursSensor': 24})
        responsePM25 = requests.get(BASE_URL + GET_MEASUREMENT_PROM, params={'name': qhawax_name, 'sensor': 'PM25', 'hoursSensor': 24})
        responseSO2 = requests.get(BASE_URL + GET_MEASUREMENT_PROM, params={'name': qhawax_name, 'sensor': 'SO2', 'hoursSensor': 24})
        responseO3 = requests.get(BASE_URL + GET_MEASUREMENT_PROM, params={'name': qhawax_name, 'sensor': 'O3', 'hoursSensor': 8})
        responseH2S = requests.get(BASE_URL + GET_MEASUREMENT_PROM, params={'name': qhawax_name, 'sensor': 'H2S', 'hoursSensor': 24})

        valueH2S = math.floor(float(responseH2S.text) * factor_final_H2S)
        valueCO = math.floor(float(responseCO.text) * factor_final_CO)
        valueNO2 = math.floor(float(responseNO2.text) * factor_final_NO2)
        valuePM10 = math.floor(float(responsePM10.text) * factor_final_PM10)
        valuePM25 = math.floor(float(responsePM25.text) * factor_final_PM25)
        valueSO2 = math.floor(float(responseSO2.text) * factor_final_SO2)
        valueO3 = math.floor(float(responseO3.text) * factor_final_O3)
        
        aux = 0
        calInca = 0
        aux = validaH2S(valueH2S)
        if aux > calInca:
            calInca = aux
            
        aux = validaCO_NO2(valueCO)
        if aux > calInca:
            calInca = aux

        aux = validaCO_NO2(valueNO2)
        if aux > calInca:
            calInca = aux

        aux = validaPM10(valuePM10)
        if aux > calInca:
            calInca = aux

        aux = validaPM25(valuePM25)
        if aux > calInca:
            calInca = aux

        aux = validaSO2(valueSO2)
        if aux > calInca:
            calInca = aux

        aux = validaO3(valueO3)
        if aux > calInca:
            calInca = aux

        name_qhawax = qhawax_name

        response = requests.post(BASE_URL + MAININCA_DATA_ENDPOINT, json ={'name': name_qhawax, 'value_inca': calInca})
        
    except Exception as e:
        print(e)