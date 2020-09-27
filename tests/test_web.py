import flask_login

from tests.fixtures import *


def test_get_article(client):
    result = client.get("/article/")
    assert result.status_code == 200


def test_admin_login(client, admin):
    result = client.post("/fellow/login", data={
        "email": "admin@example.com",
        "password": "admin",
    })
    assert result.status_code in (200, 302)
    assert flask_login.current_user.is_authenticated
    assert flask_login.current_user.email == "admin@example.com"


def test_user_login(client, admin, users):
    result = client.post("/fellow/login", data={
        "email": "user2@example.com",
        "password": "user2",
    })
    assert result.status_code in (200, 302)
    assert flask_login.current_user.is_authenticated
    assert flask_login.current_user.email == "user2@example.com"


def test_user_login_invalid_password(client, admin, users):
    result = client.post("/fellow/login", data={
        "email": "user3@example.com",
        "password": "grabage",
    })
    assert result.status_code in (200, 302)
    assert not flask_login.current_user.is_authenticated


def test_blank_user_login(client, blank_user):
    result = client.post("/fellow/login", data={
        "email": "blank_user@example.com",
        "password": "blank_user",
    })
    assert result.status_code in (200, 302)
    assert flask_login.current_user.is_authenticated
    assert flask_login.current_user.email == "blank_user@example.com"
