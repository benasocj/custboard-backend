from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.update({
    'SQLALCHEMY_DATABASE_URI': 'sqlite://',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'RESTFUL_JSON': {'indent': 2, 'sort_keys': True},
    })
app.config.from_envvar('CUSTBOARD_CONF', True)

d = SQLAlchemy(app)
api = Api(app)

# Load routes
import custboard.api
