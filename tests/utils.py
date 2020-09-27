import flask_login
import lada.models
import logging

from lada.dike import maintenance

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


def web_dike_begin_election(client):
    return client.post("/dike/panel", data={
        "begin_election": True,
    })


def web_dike_begin_voting(client):
    return client.post("/dike/panel", data={
        "begin_voting": True,
    })


def web_dike_end_voting(client):
    return client.post("/dike/panel", data={
        "begin_voting": True,
    })


def web_dike_register(client, candidate, positions, password=None):
    password = password or get_default_password(flask_login.current_user.email)
    data = {
        "kmsid": candidate.id,
        "password": password,
    }

    for position in positions:
        data[position] = True

    client.post("/dike/register", data=data)


def web_dike_ballot(client, preferences, kmsid=None, password=None):
    kmsid = kmsid or flask_login.current_user.id
    password = password or get_default_password(flask_login.current_user.email)

    data = {
        "kmsid": kmsid,
        "password": password,
    }

    election = maintenance.get_election()

    for preference in preferences:
        positions = election.positions.filter_by(name=preference["position"]).all()
        assert len(positions) == 1
        position = positions[0]
        fellow = preference["fellow"]
        rank = preference["rank"]

        data[f"{position.id}+{fellow.id}"] = rank

    log.debug(f"ballot data = {data}")
    client.post("/dike/ballot", data=data)
