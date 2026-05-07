import logging
import os
import threading
from flask import Flask, send_from_directory
from flask_socketio import SocketIO

logger = logging.getLogger(__name__)

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

    # Eager catalog warm-up: run the (potentially slow) DB init + catalog
    # build in a daemon thread so the first /api/cards/all request doesn't
    # pay the 25-second cold-start cost. Tests opt out via SKIP_CATALOG_WARMUP
    # (config flag or env var) — most pytest fixtures do, so they don't pay
    # the catalog build cost they don't need.
    skip_warmup = app.config.get(
        'SKIP_CATALOG_WARMUP',
        bool(os.environ.get('SKIP_CATALOG_WARMUP')),
    )
    if not skip_warmup:
        threading.Thread(
            target=_warmup_catalog,
            name='catalog-warmup',
            daemon=True,
        ).start()

    return app


def _warmup_catalog():
    """Pre-populate the catalog cache so the first user request is fast."""
    try:
        from . import card_catalog
        card_catalog.build_catalog()
        logger.info("catalog warm-up complete")
    except Exception:  # noqa: BLE001 — daemon thread, must not crash app
        logger.exception("catalog warm-up failed")
