from flask import Flask
from config import Config
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
app.config.from_object(Config)
cors = CORS(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models, errors, api, auth, util
app.register_blueprint(api.api_bp, name='api')
app.register_blueprint(auth.auth_bp, name='auth')
