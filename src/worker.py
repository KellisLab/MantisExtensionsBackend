from dotenv import load_dotenv
from src.app import create_app

load_dotenv ()
load_dotenv (".env.development", override=True) # Load dev if it exists

app, celery = create_app ()