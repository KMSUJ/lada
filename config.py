import os

import lada.git

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
  SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key'
   
  # articles
  ARTICLE_PER_PAGE = 12

  # database
  # change this to postgres
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'lada.db')
  SQLALCHEMY_TRACK_MODIFICATIONS = False

  # email
  MAIL_SERVER = os.environ.get('MAIL_SERVER')
  MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
  MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
  MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
  MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

  FEATURE_FLAGS = {
    'stv_rejection': True,
    'demo': False,
    'dike_candidate_board_covision_conflict_forbidden': True,
  }

  VERSION = lada.git.get_revision_hash()
