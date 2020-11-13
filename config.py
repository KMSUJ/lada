import os

import lada.git
from lada.constants import *

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)

    # articles
    ARTICLE_PER_PAGE = 12

    # database
    # change this to postgres
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'lada.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # email
    SERVER_NAME = os.environ.get('SERVER_NAME') or 'kmsuj.matinf.uj.edu.pl'
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'localhost'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    FEATURE_FLAGS = {
        FEATURE_DEMO: False,
        FEATURE_DIKE_CANDIDATE_BOARD_COVISION_CONFLICT_FORBIDDEN: True,
        FEATURE_EMAIL_VERIFICATION: True,
        FEATURE_MULTITHREADING: False,
        FEATURE_STV_REJECTION: False,
    }

    VERSION = lada.git.get_revision_hash()
