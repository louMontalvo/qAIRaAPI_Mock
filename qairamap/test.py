from flask import Flask
from flask_restful import Resource, Api
from flask import jsonify, make_response

app = Flask(__name__)
api = Api(app)


class Hello(Resource):
    def get(self, name):
        return {"Hello":name}

class Qhawax(Resource):
	def get(self):
	    qhawax_list = "[{'name': 'qH001', 'location': {'lat': -12.073235, 'lon': -77.081671}, 'main_aqi': None, 'main_inca': 150}, {'name': 'qH002', 'location': {'lat': -12.10007, 'lon': -76.98912}, 'main_aqi': None, 'main_inca': 200}, {'name': 'qH003', 'location': {'lat': -12.095867, 'lon': -76.98912}, 'main_aqi': None, 'main_inca': 50}, {'name': 'qH004', 'location': {'lat': -12.103215, 'lon': -76.980326}, 'main_aqi': None, 'main_inca': 0}, {'name': 'qH005', 'location': {'lat': -12.073174, 'lon': -77.081994}, 'main_aqi': None, 'main_inca': 1000}, {'name': 'qH006', 'location': {'lat': -12.073174, 'lon': -77.081988}, 'main_aqi': None, 'main_inca': 350}, {'name': 'qH007', 'location': {'lat': -12.073173, 'lon': -77.081993}, 'main_aqi': None, 'main_inca': 100}, {'name': 'qH008', 'location': {'lat': -12.073174, 'lon': -77.081994}, 'main_aqi': None, 'main_inca': 2500}, {'name': 'qH009', 'location': {'lat': -12.073174, 'lon': -77.081994}, 'main_aqi': None, 'main_inca': 5}, {'name': 'qH010', 'location': {'lat': -12.073174, 'lon': -77.081994}, 'main_aqi': None, 'main_inca': 45}, {'name': 'qH011', 'location': {'lat': -12.102992, 'lon': -76.989268}, 'main_aqi': None, 'main_inca': 50}, {'name': 'qH012', 'location': {'lat': -12.073174, 'lon': -77.081994}, 'main_aqi': None, 'main_inca': 150}, {'name': 'qH013', 'location': {'lat': -12.073174, 'lon': -77.081994}, 'main_aqi': None, 'main_inca': 90}]"
	    return make_response(jsonify(qhawax_list), 200)

api.add_resource(Qhawax, '/getAllQhawax')
api.add_resource(Hello, '/hello/<name>')

# at URL http://localhost:5000/getAllQhawax

if __name__ == '__main__':
 app.run(debug=True)