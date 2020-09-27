import datetime
import logging

from flask import Blueprint

from lada import db
from lada.models import Fellow

bp = Blueprint('fellow', __name__)

from lada.fellow import routes

log = logging.getLogger(__name__)


def register(email, password=None, **kwords):
  fellow = Fellow(email=email, **kwords)
  fellow.joined = datetime.datetime.utcnow()

  if password is not None:
    fellow.set_password(password)

  db.session.add(fellow)

  log.info(f'New user registered: {fellow}')

  return fellow
