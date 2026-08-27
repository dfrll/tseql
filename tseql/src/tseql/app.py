#! /usr/bin/env python3
import logging
import structlog
from flask import Flask
from flask_cors import CORS
from .routes import api


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
    )

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("werkzeug").setLevel(logging.WARNING)

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(
                fmt="%Y-%m-%d %H:%M:%S",
                utc=False,
            ),
            structlog.processors.add_log_level,
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
    )


def create_app():
    setup_logging()

    # tool registration
    from . import tools

    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(api, url_prefix="/api")
    return app
