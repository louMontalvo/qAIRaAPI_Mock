from flask import Flask
from flask_jsglue import JSGlue
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

# Config
app = Flask(__name__)
app.config.from_object('config')
socketio = SocketIO(app)

# Extensions
db = SQLAlchemy(app)
jsglue = JSGlue(app)
login_manager = LoginManager()
login_manager.init_app(app)
migrate = Migrate(app, db)

from project.main import gas_sensor, processed_measurement, qhawax, air_quality
import project.database.models as models
from project.database.models import Company, User, Qhawax , ProcessedMeasurement, AirQualityMeasurement

db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)