from flask import Blueprint

bp = Blueprint('article', __name__)

from lada.article import routes
