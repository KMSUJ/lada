import flask_login
import lada.models
import logging

log = logging.getLogger(__name__)


def get_default_password(email):
    base = email.split("@")[0]
    password = f"{base}_password"
    return password


def web_login(client, fellow=None, email=None, password=None):
    email = email or fellow.email
    password = password or get_default_password(email)

    client.get("/fellow/logout")
    return client.post("/fellow/login", data={
        "email": email,
        "password": password,
    })
