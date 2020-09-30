import tempfile

import pytest

import lada
import lada.fellow
import tests.utils
from lada.constants import *


@pytest.fixture
def app():
    app = lada.create_app()

    db_fd, db_path = tempfile.mkstemp()
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        lada.db.create_all()

        yield app


@pytest.fixture
def client(app):
    client = app.test_client()
    with client:
        yield client


class FeatureFlagsHandler:
    def __init__(self, feature_flags=None):
        self.feature_flags = feature_flags or {}

    def handler(self, flag):
        return self.feature_flags.get(flag, False)

    def enable(self, flag):
        self.feature_flags[flag] = True

    def disable(self, flag):
        self.feature_flags[flag] = False


@pytest.fixture
def feature_flags(app):
    feature_flags_handler = FeatureFlagsHandler(app.config["FEATURE_FLAGS"])
    lada.feature_flags.clear_handlers()
    lada.feature_flags.add_handler(feature_flags_handler.handler)
    return feature_flags_handler


@pytest.fixture()
def admin(app):
    base = "admin"
    email = f"{base}@example.com"
    password = tests.utils.get_default_password(email)

    admin = lada.fellow.register(
        email=email,
        password=password,
        name=base,
    )
    admin.set_board(FELLOW_ACTIVE, True)
    admin.set_board(FELLOW_FELLOW, True)
    admin.set_board(FELLOW_BOARD, True)
    admin.set_board(POSITION_BOSS, True)

    return admin


@pytest.fixture()
def blank_user(app):
    base = "blank_user"
    email = f"{base}@example.com"
    password = tests.utils.get_default_password(email)

    user = lada.fellow.register(
        email=email,
        password=password,
        name=base,
    )

    return user


@pytest.fixture()
def users(app):
    result = []

    for i in range(15):
        base = f"user{i}"
        email = f"{base}@example.com"
        password = tests.utils.get_default_password(email)

        user = lada.fellow.register(
            email=email,
            password=password,
            name=base,
        )
        user.set_board(FELLOW_ACTIVE, True)
        user.set_board(FELLOW_FELLOW, True)

        result.append(user)

    return result
