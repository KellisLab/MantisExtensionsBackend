import os

class Config:
    DEBUG = False
    TESTING = False
    ENV = 'production'

class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'

class ProductionConfig(Config):
    pass

def get_config():
    debug = os.environ.get('FLASK_DEBUG')
    
    if debug:
        return DevelopmentConfig
    
    return ProductionConfig