import flask_login

from tests.fixtures import *


def test_get_article(client):
    result = client.get("/article/")
    assert result.status_code == 200


def test_admin_login(client, admin):
    email = "admin@example.com"
    password = tests.utils.get_default_password(email)

    result = tests.utils.web_login(client, email=email, password=password)

    assert result.status_code in (200, 302)
    assert flask_login.current_user.is_authenticated
    assert flask_login.current_user.email == "admin@example.com"


def test_user_login(client, admin, users):
    email = "user2@example.com"
    password = "changed_password"
    users[2].set_password(password)

    result = tests.utils.web_login(client, email=email, password=password)
    assert result.status_code in (200, 302)
    assert flask_login.current_user.is_authenticated
    assert flask_login.current_user.email == "user2@example.com"


def test_user_login_invalid_password(client, admin, users):
    email = "user3@example.com"
    password = "grabage"

    result = tests.utils.web_login(client, email=email, password=password)
    assert result.status_code in (200, 302)
    assert not flask_login.current_user.is_authenticated


def test_blank_user_login(client, blank_user):
    email = "blank_user@example.com"
    password = tests.utils.get_default_password(email)

    result = tests.utils.web_login(client, email=email, password=password)

    assert result.status_code in (200, 302)
    assert flask_login.current_user.is_authenticated
    assert flask_login.current_user.email == "blank_user@example.com"

"""
# this test will not work with cli registration
def test_registration_without_email(client, feature_flags):
    feature_flags.disable(FEATURE_EMAIL_VERIFICATION)

    email = "test_user@example.com"
    password = "password"

    data = {
        "email": email,
        "password": password,
        "repassword": password,
    }

    client.post("/fellow/register", data=data)

    tests.utils.web_login(client, email=email, password=password)

    current_user = flask_login.current_user
    assert current_user.email == email
    assert current_user.verified
"""
