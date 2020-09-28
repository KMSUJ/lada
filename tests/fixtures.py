import tempfile

import pytest

import lada
import lada.fellow
import tests.utils


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
    admin.set_board('active', True)
    admin.set_board('fellow', True)
    admin.set_board('board', True)
    admin.set_board('boss', True)

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
        user.set_board('active', True)
        user.set_board('fellow', True)

        result.append(user)

    return result
