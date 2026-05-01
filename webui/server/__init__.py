import os
from flask import Flask, send_from_directory
from flask_socketio import SocketIO

socketio = SocketIO(
    cors_allowed_origins="*",
    ping_timeout=60,
    ping_interval=25,
    async_mode='threading'  # 使用 threading 模式，更稳定
)

CLIENT_DIST = os.path.join(os.path.dirname(__file__), '..', 'client', 'dist')

def create_app():
    app = Flask(__name__, static_folder=CLIENT_DIST, static_url_path='')
    app.config['SECRET_KEY'] = 'fireplace-secret-key'

    socketio.init_app(app)

    from . import views, socket
    app.register_blueprint(views.bp)
    socket.register_socket_events(socketio)

    # SPA client-side routes fallback to index.html
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        return send_from_directory(app.static_folder, 'index.html')

    return app
