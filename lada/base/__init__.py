from flask import Blueprint

bp = Blueprint('base', __name__)

from lada.base import routes
