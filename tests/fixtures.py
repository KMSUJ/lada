import os
import tempfile
import unittest

import lada

import pytest


@pytest.fixture
def app():
  app = lada.create_app()

  db_fd, db_path = tempfile.mkstemp()
  app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
  app.config['TESTING'] = True

  with app.app_context():
    lada.db.create_all()

    yield app


@pytest.fixture
def client(app):
  client = app.test_client()
  return client


class FeatureFlagsHandler:
  def __init__(self):
    self.feature_flags = {}

  def handler(self, flag):
    return self.feature_flags.get(flag, False)

  def enable(self, flag):
    self.feature_flags[flag] = True

  def disable(self, flag):
    self.feature_flags[flag] = False

  def default(self, flag):
    del self.feature_flags[flag]


@pytest.fixture
def feature_flags(app):
  feature_flags_handler = FeatureFlagsHandler()
  lada.feature_flags.clear_handlers()
  lada.feature_flags.add_handler(feature_flags_handler.handler)
  return feature_flags_handler
