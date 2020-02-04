import os

# You need to replace the next values with the appropriate values for your configuration
SECRET_KEY = 'my_precious'
basedir = os.path.abspath(os.path.dirname(__file__))
#SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'flask_boilerplate_main.db')
SQLALCHEMY_DATABASE_URI = 'postgres://qaira:$3cq4IR4@qairamap-db.c6xdvtbzawt6.us-east-1.rds.amazonaws.com:5432/qairamap_db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
MAIL_DEFAULT_RECEIVER = 'equipos@qairadrones.com'

# Gmail authentication
ADMIN_EMAIL = os.environ.get('MAIL_USERNAME')
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')
MAIL_SENDER = os.environ.get('MAIL_USERNAME')
# Mail settings
MAIL_SERVER_PORT = 'smtp.googlemail.com:587'