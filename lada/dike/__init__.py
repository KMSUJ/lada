from flask import Blueprint

bp = Blueprint('dike', __name__)

from lada.dike import routes
