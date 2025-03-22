from dotenv import load_dotenv
import os

load_dotenv ()
load_dotenv (".env.development", override=True) # Load dev if it exists

from src.app import create_app

app, celery = create_app ()