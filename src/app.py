import argparse
import os
import logging
from dotenv import load_dotenv
from flask import Flask
from src.config import get_config
from src.extensions import cache, cors, make_celery
from src.api.routes import init_app

logging.basicConfig(level=logging.DEBUG)

def create_app(config_class=None):
    app = Flask(__name__)
    
    # Load configuration
    if config_class is None:
        config_class = get_config()

    app.config.from_object(config_class)
    
    # Initialize extensions
    cors.init_app(app)
    cache.init_app(app)
    celery = make_celery(app)
    
    init_app(app)
    
    return app, celery

if __name__ == "__main__":
    app, _ = create_app()

    app.run(host="0.0.0.0", port=8111, debug=os.environ.get("FLASK_ENV") == "development")