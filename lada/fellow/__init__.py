from flask import Blueprint

bp = Blueprint('fellow', __name__)

from lada.fellow import routes
