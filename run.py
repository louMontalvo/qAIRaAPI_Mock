from project import app, socketio

socketio.run(app,host='0.0.0.0',port=8888)