from flask import Flask
from flask_socketio import SocketIO

socketio = SocketIO(
    cors_allowed_origins="*",
    ping_timeout=60,
    ping_interval=25,
    async_mode='threading'  # 使用 threading 模式，更稳定
)

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'fireplace-secret-key'

    socketio.init_app(app)

    from . import views, socket
    app.register_blueprint(views.bp)
    socket.register_socket_events(socketio)

    return app
