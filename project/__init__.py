from flask import Flask
from flask_jsglue import JSGlue
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_cors import CORS, cross_origin

# Config
app = Flask(__name__)
app.config.from_object('config')
socketio = SocketIO(app,cors_allowed_origins="*")
CORS(app)

# Extensions
db = SQLAlchemy(app)
jsglue = JSGlue(app)
login_manager = LoginManager()
login_manager.init_app(app)
migrate = Migrate(app, db)
mail = Mail(app)

from project.main import gas_sensor, processed_measurement, qhawax, air_quality, raw_measurement,eca_noise, gas_inca, qhawax_installation_history, user
import project.database.models as models
from project.database.models import Company, User, Qhawax , ProcessedMeasurement, AirQualityMeasurement, RawMeasurement, EcaNoise, GasInca, QhawaxInstallationHistory

db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)