from flask import Flask
from config import Config
from sassutils.wsgi import SassMiddleware
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'fellow.login'
login.login_message = 'Please log in to access this page.'

def create_app(config_class=Config):
  app = Flask(__name__)
  app.config.from_object(config_class)
  app.wsgi_app = SassMiddleware(app.wsgi_app, {'lada': ('static/sass', 'static/css', '/static/css')})

  # extenstions
  db.init_app(app)
  migrate.init_app(app, db)
  login.init_app(app)

  # blueprint registrations
  from lada.base import bp as base_bp
  app.register_blueprint(base_bp)

  from lada.fellow import bp as fellow_bp
  app.register_blueprint(fellow_bp)

  return app
