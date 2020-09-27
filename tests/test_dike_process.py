from tests.fixtures import *


def test_voting(client, feature_flags):
    feature_flags.enable("demo")

    result = client.get("/fellow/seeddb")
    assert result.status_code in (200, 302)

    result = client.post("/fellow/login", data={
        "email": "admin@kms.uj.edu.pl",
        "password": "admin",
    })
    assert result.status_code in (200, 302)

    result = client.post("/dike/panel", data={
        "begin_election": True,
    })
    assert result.status_code in (200, 302)

    election = maintenance.get_election()
    print(election)

    result = client.get("/dike/seedregister")
    assert result.status_code in (200, 302)

    result = client.post("/dike/panel", data={
        "begin_voting": True,
    })
    assert result.status_code in (200, 302)

    result = client.get("/dike/seedvote")
    assert result.status_code in (200, 302)

    result = client.post("/dike/panel", data={
        "end_voting": True,
    })
    assert result.status_code in (200, 302)
def test_voting(client, feature_flags):
    feature_flags.enable("demo")

    result = client.get("/fellow/seeddb")
    assert result.status_code in (200, 302)

    result = client.post("/fellow/login", data={
        "email": "admin@kms.uj.edu.pl",
        "password": "admin",
    })
    assert result.status_code in (200, 302)

    result = client.post("/dike/panel", data={
        "begin_election": True,
    })
    assert result.status_code in (200, 302)

    election = maintenance.get_election()
    print(election)

    result = client.get("/dike/seedregister")
    assert result.status_code in (200, 302)

    result = client.post("/dike/panel", data={
        "begin_voting": True,
    })
    assert result.status_code in (200, 302)

    result = client.get("/dike/seedvote")
    assert result.status_code in (200, 302)

    result = client.post("/dike/panel", data={
        "end_voting": True,
    })
    assert result.status_code in (200, 302)
