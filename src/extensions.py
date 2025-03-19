from flask_caching import Cache
from flask_cors import CORS
from celery import Celery
import os

cache = Cache()
cors = CORS()
celery = Celery()

def make_celery(app):
    celery.conf.update(
        broker_url=os.environ.get('CELERY_BROKER_URL'),
        result_backend=os.environ.get('CELERY_RESULT_BACKEND')
    )
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery