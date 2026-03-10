from flask import Flask
from flask_socketio import SocketIO

socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'fireplace-secret-key'

    socketio.init_app(app, cors_allowed_origins="*")

    from . import views, socket
    app.register_blueprint(views.bp)
    socket.register_socket_events(socketio)

    return app
