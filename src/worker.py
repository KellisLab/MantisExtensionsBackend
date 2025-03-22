from dotenv import load_dotenv
import os

load_dotenv ()

if os.environ.get ("FLASK_ENV") != "production":
    load_dotenv (".env.development", override=True)

from src.app import create_app

app, celery = create_app ()