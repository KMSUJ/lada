import logging
import re
import tests.utils

from lada.dike import maintenance
from tests.fixtures import *

log = logging.getLogger(__name__)


def test_start_election(client, blank_user):
    blank_user.set_board("board", True)

    tests.utils.web_login(client, blank_user)

    assert maintenance.get_election() is None

    result = tests.utils.web_dike_begin_election(client)

    assert result.status_code in (200, 302)
    assert maintenance.get_election() is not None


def test_register_candidates(client, blank_user, users):
    blank_user.set_board("board", True)

    tests.utils.web_login(client, blank_user)

    maintenance.begin_election()

    tests.utils.web_dike_register(client, users[0], ["boss", "vice", "free"])
    tests.utils.web_dike_register(client, users[1], ["boss", "treasure", "library", "free"])
    tests.utils.web_dike_register(client, users[2], ["covision"])

    election = maintenance.get_election()
    assert set(election.positions.filter_by(name="boss").first().candidates.all()) == {users[0], users[1]}
    assert set(election.positions.filter_by(name="vice").first().candidates.all()) == {users[0]}
    assert set(election.positions.filter_by(name="treasure").first().candidates.all()) == {users[1]}
    assert set(election.positions.filter_by(name="secret").first().candidates.all()) == set()
    assert set(election.positions.filter_by(name="library").first().candidates.all()) == {users[1]}
    assert set(election.positions.filter_by(name="free").first().candidates.all()) == {users[0], users[1]}
    assert set(election.positions.filter_by(name="covision").first().candidates.all()) == {users[2]}


def test_register_candidates_without_free(client, blank_user, users):
    blank_user.set_board("board", True)

    tests.utils.web_login(client, blank_user)

    maintenance.begin_election()

    tests.utils.web_dike_register(client, users[0], ["boss", "vice", "free"])
    tests.utils.web_dike_register(client, users[1], ["boss", "vice"])

    election = maintenance.get_election()
    assert set(election.positions.filter_by(name="boss").first().candidates.all()) == {users[0]}


def test_election_determinism(client, blank_user, users):
    blank_user.set_board("board", True)

    tests.utils.web_login(client, blank_user)

    tests.utils.web_dike_begin_election(client)

    tests.utils.web_dike_register(client, users[0], ["boss", "free"])
    tests.utils.web_dike_register(client, users[1], ["boss", "free"])

    tests.utils.web_dike_begin_voting(client)

    tests.utils.web_login(client, users[0])
    tests.utils.web_dike_ballot(client, [
        {
            "fellow": users[0],
            "position": "boss",
            "rank": 1,
        },
    ])

    tests.utils.web_login(client, users[1])
    tests.utils.web_dike_ballot(client, [
        {
            "fellow": users[1],
            "position": "boss",
            "rank": 1,
        },
    ])

    tests.utils.web_login(client, blank_user)
    tests.utils.web_dike_end_voting(client)

    response = client.get("/dike/reckoning")
    first_election_order = re.findall(rb"<label>(user\w).*?</label>", response.data)

    for _ in range(8):  # If it is undeterministic, there is almost 100% probability it fails
        response = client.get("/dike/reckoning")
        election_order = re.findall(rb"<label>(user\w).*?</label>", response.data)
        assert election_order == first_election_order


def test_election_missing_unvoted_candidate(client, blank_user, users):
    blank_user.set_board("board", True)

    tests.utils.web_login(client, blank_user)

    tests.utils.web_dike_begin_election(client)

    tests.utils.web_dike_register(client, users[0], ["boss", "free"])
    tests.utils.web_dike_register(client, users[1], ["boss", "free"])

    tests.utils.web_dike_begin_voting(client)

    tests.utils.web_login(client, users[0])
    tests.utils.web_dike_ballot(client, [
        {
            "fellow": users[0],
            "position": "boss",
            "rank": 1,
        },
    ])

    tests.utils.web_login(client, blank_user)
    tests.utils.web_dike_end_voting(client)

    response = client.get("/dike/reckoning")
    election_order = re.findall(rb"<label>(user\w).*?</label>", response.data)

    assert b"user0" in election_order
    assert b"user1" in election_order


def test_election_candidate_injection(client, blank_user, users):
    blank_user.set_board("board", True)

    tests.utils.web_login(client, blank_user)

    tests.utils.web_dike_begin_election(client)

    tests.utils.web_dike_register(client, users[0], ["boss", "free"])

    tests.utils.web_dike_begin_voting(client)

    tests.utils.web_login(client, users[0])
    tests.utils.web_dike_ballot(client, [
        {
            "fellow": users[0],
            "position": "boss",
            "rank": 1,
        },
    ])

    tests.utils.web_login(client, users[1])
    tests.utils.web_dike_ballot(client, [
        {
            "fellow": users[1],
            "position": "boss",
            "rank": 1,
        },
    ])

    tests.utils.web_login(client, blank_user)
    tests.utils.web_dike_end_voting(client)

    response = client.get("/dike/reckoning")
    election_order = re.findall(rb"<label>(user\w).*?</label>", response.data)

    assert b"user0" in election_order
    assert b"user1" not in election_order
