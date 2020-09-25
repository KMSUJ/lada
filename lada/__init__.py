import logging

from flask import Flask
from config import Config
from sassutils.wsgi import SassMiddleware
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_pagedown import PageDown
from flask_featureflags import FeatureFlag
from flaskext.markdown import Markdown

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'fellow.login'
login.login_message = 'Please log in to access this page.'
mail = Mail()
pagedown = PageDown()
markdown = Markdown()
feature_flags = FeatureFlag()

def create_app(config_class=Config):
  app = Flask(__name__)
  app.logger.info(f'Starting application')
  app.config.from_object(config_class)
  app.wsgi_app = SassMiddleware(
    app.wsgi_app,
    {
      'lada': {
        'sass_path': 'static/sass',
        'css_path': 'static/css',
        'wsgi_path': '/static/css',
        'strip_extension': False
      },
    }
  )

  # extenstions
  db.init_app(app)
  migrate.init_app(app, db)
  login.init_app(app)
  mail.init_app(app)
  pagedown.init_app(app)
  markdown.init_app(app)
  feature_flags.init_app(app)

  # blueprint registrations
  from lada.base import bp as base_bp
  app.register_blueprint(base_bp)

  from lada.article import bp as article_bp
  app.register_blueprint(article_bp, url_prefix='/article')

  from lada.fellow import bp as fellow_bp
  app.register_blueprint(fellow_bp, url_prefix='/fellow')

  from lada.dike import bp as dike_bp
  app.register_blueprint(dike_bp, url_prefix='/dike')

  return app
