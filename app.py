import os
from dotenv import load_dotenv

load_dotenv()

from models import db

from flask import Flask
from fortinet_api_1_0 import blueprint as api
from caching import cache
from urllib.parse import quote

class BaseConfig(object):   
    SQLALCHEMY_TRACK_MODIFICATIONS = False     
    CACHE_TYPE = "RedisCache"
    CACHE_KEY_PREFIX = "fortine_api_"
    CACHE_DEFAULT_TIMEOUT = os.environ.get('CACHE_DEFAULT_TIMEOUT')
    CACHE_REDIS_HOST = os.environ.get('CACHE_REDIS_HOST')
    CACHE_REDIS_PORT = int(os.environ.get('CACHE_REDIS_PORT'))
    CACHE_REDIS_DB = int(os.environ.get('CACHE_REDIS_DB'))
    CACHE_REDIS_URL = os.environ.get('CACHE_REDIS_URL')
    SQLALCHEMY_DATABASE_URI =  os.environ.get('SQLALCHEMY_DATABASE_URI') % quote(os.environ.get('DB_PASS'))
   
def create_app():
    app = Flask(__name__)
    app.config.from_object(BaseConfig)
    return app

    
def register_extensions(app):
    db.init_app(app)
    db.app = app
    cache.init_app(app)
    return app


app = create_app()

register_extensions(app)
app.register_blueprint(api)


