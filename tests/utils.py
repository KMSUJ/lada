import flask_login
import lada.models
import logging

from lada.dike.maintenance import get_election

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
        "begin_voting_boss": True,
    })


def web_dike_begin_voting_board(client):
    return client.post("/dike/panel", data={
        "begin_voting_board": True,
    })


def web_dike_begin_voting_covision(client):
    return client.post("/dike/panel", data={
        "begin_voting_covision": True,
    })


def web_dike_end_voting(client):
    return client.post("/dike/panel", data={
        "end_voting": True,
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

    election = get_election()

    for preference in preferences:
        positions = election.positions.filter_by(name=preference["position"]).all()
        assert len(positions) == 1
        position = positions[0]
        fellow = preference["fellow"]
        rank = preference["rank"]

        data[f"{position.id}+{fellow.id}"] = rank

    log.debug(f"ballot data = {data}")
    client.post("/dike/ballot", data=data)


def web_dike_reckon_boss(client):
    return client.post("/dike/reckoning", data={
        "choose_boss": True,
    })


def web_dike_reckon_board(client, preferences, password=None):
    password = password or get_default_password(flask_login.current_user.email)

    data = {
        "password": password,
    }

    for preference in preferences:
        position = preference["position"]
        fellows = preference["fellows"]

        data[position] = "+".join(str(fellow.id) for fellow in fellows)

    log.debug(f"reckon data = {data}")
    client.post("/dike/reckoning", data=data)


def web_dike_reckon_covision(client):
    return client.post("/dike/reckoning", data={
        "choose_covision": True,
    })
