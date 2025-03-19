import os

class Config:
    CACHE_TYPE = 'simple'
    DEBUG = False
    TESTING = False
    ENV = 'production'

class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'

class ProductionConfig(Config):
    pass

def get_config():
    env = os.environ.get('FLASK_ENV', 'development')
    
    if env == 'production':
        return ProductionConfig
    
    return DevelopmentConfig