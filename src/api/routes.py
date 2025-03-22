from flask import Blueprint
from src.api.space import space
from src.api.get_proxy import get_proxy

api = Blueprint('api', __name__)

def init_app(app):
    app.register_blueprint(space, url_prefix='/api')
    app.register_blueprint(get_proxy, url_prefix='/api')