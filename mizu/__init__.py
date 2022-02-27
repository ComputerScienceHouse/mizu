import os
import sys
import json
import logging

from flask import Flask
from flask import jsonify
from flask import request
from flask import session
from flask import redirect

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from csh_ldap import CSHLDAP
import ldap

from mizu import config

if os.environ.get("LDAP_DEBUG") == "true":
    ldap.set_option(ldap.OPT_DEBUG_LEVEL, 255)

logger = logging.getLogger(__name__)


app = Flask(__name__)
app.config.update({
    'SQLALCHEMY_TRACK_MODIFICATIONS': False
})

app.config.from_object(config)
if os.path.exists(os.path.join(os.getcwd(), 'config.py')):
    app.config.from_pyfile(os.path.join(os.getcwd(), 'config.py'))

app.secret_key = app.config['SECRET_KEY']

if app.config['DEBUG']:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
else:
    logger.setLevel(logging.INFO)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

mock_db = None
if os.path.exists(os.path.join(os.getcwd(), 'mock.json')):
    with open('mock.json', 'r') as f:
        mock_db = json.load(f)

from mizu.models import Machine
from mizu.models import Item
from mizu.models import Slot
from mizu.models import Temp
from mizu.models import Log

ldap = CSHLDAP(app.config['LDAP_BIND_DN'],
               app.config['LDAP_BIND_PW'])

from mizu.auth import check_token

from mizu.drinks import drinks_bp
from mizu.items import items_bp
from mizu.users import users_bp
from mizu.slots import slots_bp

from mizu.data_adapters import SqlAlchemyAdapter, MockAdapter

app.register_blueprint(drinks_bp)
app.register_blueprint(items_bp)
app.register_blueprint(users_bp)
app.register_blueprint(slots_bp)

@app.route('/')
def hello_world():
    return redirect('https://webdrink.csh.rit.edu', 302)

@app.errorhandler(404)
def handle_404(e):
    error = {
        "message": "What you're looking for does not exist, like a drink admin when drink is empty",
        "error": str(e),
        "errorCode": 404,
    }

    return jsonify(error), 404

@app.errorhandler(500)
def handle_500(e):
    error = {
        "message": "The drink server encountered an error, it was more than likely your fault",
        "error": str(e),
        "errorCode": 500,
    }

    return jsonify(error), 500

@app.after_request
def allow_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE'
    return response

