import lada.models
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


def test_register_candidates_board_covision_conflict(client, blank_user, users):
    blank_user.set_board("board", True)

    tests.utils.web_login(client, blank_user)

    maintenance.begin_election()

    tests.utils.web_dike_register(client, users[0], ["boss", "free"])
    tests.utils.web_dike_register(client, users[1], ["boss", "free", "covision"])

    election = maintenance.get_election()
    assert set(election.positions.filter_by(name="boss").first().candidates.all()) == {users[0]}


def test_register_candidates_board_positions_number_exceeded(client, blank_user, users):
    blank_user.set_board("board", True)

    tests.utils.web_login(client, blank_user)

    maintenance.begin_election()

    tests.utils.web_dike_register(client, users[0], ["boss", "vice", "treasure", "free"])
    tests.utils.web_dike_register(client, users[1], ["boss", "vice", "treasure", "secret", "free"])

    election = maintenance.get_election()
    assert set(election.positions.filter_by(name="boss").first().candidates.all()) == {users[0]}


def test_register_candidates_multi_registration(client, blank_user, users):
    blank_user.set_board("board", True)

    tests.utils.web_login(client, blank_user)

    maintenance.begin_election()

    tests.utils.web_dike_register(client, users[0], ["boss", "free"])
    tests.utils.web_dike_register(client, users[0], ["vice", "free"])

    election = maintenance.get_election()
    assert set(election.positions.filter_by(name="boss").first().candidates.all()) == {users[0]}
    assert set(election.positions.filter_by(name="vice").first().candidates.all()) == set()
    assert set(election.positions.filter_by(name="free").first().candidates.all()) == {users[0]}


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


def test_election_ballot_rank_duplicate(client, blank_user, users):
    blank_user.set_board("board", True)

    tests.utils.web_login(client, blank_user)

    tests.utils.web_dike_begin_election(client)

    tests.utils.web_dike_register(client, users[0], ["boss", "free"])
    tests.utils.web_dike_register(client, users[1], ["boss", "free"])

    tests.utils.web_dike_begin_voting(client)

    assert len(lada.models.Vote.query.all()) == 0

    tests.utils.web_login(client, users[0])
    tests.utils.web_dike_ballot(client, [
        {
            "fellow": users[0],
            "position": "boss",
            "rank": 1,
        },
        {
            "fellow": users[1],
            "position": "boss",
            "rank": 1,
        },
    ])

    assert len(lada.models.Vote.query.all()) == 0


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


def test_election_reckoning(client, blank_user, users):
    blank_user.set_board("board", True)

    tests.utils.web_login(client, blank_user)

    tests.utils.web_dike_begin_election(client)

    tests.utils.web_dike_register(client, users[0], ["boss", "free"])
    tests.utils.web_dike_register(client, users[1], ["vice", "free"])
    tests.utils.web_dike_register(client, users[2], ["treasure", "free"])
    tests.utils.web_dike_register(client, users[3], ["secret", "free"])
    tests.utils.web_dike_register(client, users[4], ["library", "free"])
    tests.utils.web_dike_register(client, users[5], ["free"])
    tests.utils.web_dike_register(client, users[6], ["free"])
    tests.utils.web_dike_register(client, users[7], ["free"])
    tests.utils.web_dike_register(client, users[8], ["covision"])
    tests.utils.web_dike_register(client, users[9], ["covision"])
    tests.utils.web_dike_register(client, users[10], ["covision"])

    tests.utils.web_dike_register(client, users[11], ["vice", "free"])
    tests.utils.web_dike_register(client, users[12], ["treasure", "free"])

    tests.utils.web_dike_begin_voting(client)

    tests.utils.web_login(client, users[0])
    tests.utils.web_dike_ballot(client, [
        {"fellow": users[0], "position": "boss", "rank": 1},
        {"fellow": users[1], "position": "vice", "rank": 1},
        {"fellow": users[2], "position": "treasure", "rank": 1},
        {"fellow": users[3], "position": "secret", "rank": 1},
        {"fellow": users[4], "position": "library", "rank": 1},
        {"fellow": users[5], "position": "free", "rank": 1},
        {"fellow": users[6], "position": "free", "rank": 2},
        {"fellow": users[7], "position": "free", "rank": 3},
        {"fellow": users[8], "position": "covision", "rank": 1},
        {"fellow": users[9], "position": "covision", "rank": 2},
        {"fellow": users[10], "position": "covision", "rank": 3},

    ])

    tests.utils.web_login(client, users[1])
    tests.utils.web_dike_ballot(client, [
        {"fellow": users[11], "position": "vice", "rank": 1},
        {"fellow": users[12], "position": "treasure", "rank": 1},
    ])

    tests.utils.web_login(client, blank_user)
    tests.utils.web_dike_end_voting(client)

    client.get("/dike/reckoning")

    election = maintenance.get_election()
    positions = election.positions.all()
    for position in positions:
        assert position.is_reckoned

    tests.utils.web_dike_reckon(client, [
        {"position": "boss", "fellows": [users[0]]},
        {"position": "vice", "fellows": [users[11]]},
        {"position": "treasure", "fellows": [users[2]]},
        {"position": "secret", "fellows": [users[3]]},
        {"position": "library", "fellows": [users[4]]},
        {"position": "free", "fellows": [users[1], users[6], users[7]]},
        {"position": "covision", "fellows": [users[8], users[9], users[10]]},
    ])

    assert users[0].check_board("boss")
    assert users[0].check_board("board")
    assert users[11].check_board("vice")
    assert users[11].check_board("board")
    assert users[2].check_board("treasure")
    assert users[2].check_board("board")
    assert users[3].check_board("secret")
    assert users[3].check_board("board")
    assert users[4].check_board("library")
    assert users[4].check_board("board")
    assert users[1].check_board("free")
    assert users[1].check_board("board")
    assert users[6].check_board("free")
    assert users[6].check_board("board")
    assert users[7].check_board("free")
    assert users[7].check_board("board")
    assert users[8].check_board("covision")
    assert users[9].check_board("covision")
    assert users[10].check_board("covision")

    assert not users[12].check_board("treasure")
    assert not users[12].check_board("board")


def test_election_reckoning_candidate_injection(client, blank_user, users):
    blank_user.set_board("board", True)

    tests.utils.web_login(client, blank_user)

    tests.utils.web_dike_begin_election(client)

    tests.utils.web_dike_register(client, users[0], ["boss", "free"])
    tests.utils.web_dike_register(client, users[1], ["vice", "free"])
    tests.utils.web_dike_register(client, users[2], ["treasure", "free"])
    tests.utils.web_dike_register(client, users[3], ["secret", "free"])
    tests.utils.web_dike_register(client, users[4], ["library", "free"])
    tests.utils.web_dike_register(client, users[5], ["free"])
    tests.utils.web_dike_register(client, users[6], ["free"])
    tests.utils.web_dike_register(client, users[7], ["free"])
    tests.utils.web_dike_register(client, users[8], ["covision"])
    tests.utils.web_dike_register(client, users[9], ["covision"])
    tests.utils.web_dike_register(client, users[10], ["covision"])

    tests.utils.web_dike_begin_voting(client)

    tests.utils.web_login(client, users[0])
    tests.utils.web_dike_ballot(client, [
        {"fellow": users[0], "position": "boss", "rank": 1},
        {"fellow": users[1], "position": "vice", "rank": 1},
        {"fellow": users[2], "position": "treasure", "rank": 1},
        {"fellow": users[3], "position": "secret", "rank": 1},
        {"fellow": users[4], "position": "library", "rank": 1},
        {"fellow": users[5], "position": "free", "rank": 1},
        {"fellow": users[6], "position": "free", "rank": 1},
        {"fellow": users[7], "position": "free", "rank": 1},
        {"fellow": users[8], "position": "covision", "rank": 1},
        {"fellow": users[9], "position": "covision", "rank": 1},
        {"fellow": users[10], "position": "covision", "rank": 1},

    ])

    tests.utils.web_login(client, blank_user)
    tests.utils.web_dike_end_voting(client)

    client.get("/dike/reckoning")

    tests.utils.web_dike_reckon(client, [
        {"position": "boss", "fellows": [users[0]]},
        {"position": "vice", "fellows": [users[11]]},  # injection
        {"position": "treasure", "fellows": [users[2]]},
        {"position": "secret", "fellows": [users[3]]},
        {"position": "library", "fellows": [users[4]]},
        {"position": "free", "fellows": [users[5], users[6], users[7]]},
        {"position": "covision", "fellows": [users[8], users[9], users[10]]},
    ])

    assert not users[11].check_board("vice")
    assert not users[11].check_board("board")

    assert not users[0].check_board("boss")
    assert not users[0].check_board("board")


def test_election_reckoning_candidate_boss_change(client, blank_user, users):
    blank_user.set_board("board", True)

    tests.utils.web_login(client, blank_user)

    tests.utils.web_dike_begin_election(client)

    tests.utils.web_dike_register(client, users[0], ["boss", "free"])
    tests.utils.web_dike_register(client, users[1], ["vice", "free"])
    tests.utils.web_dike_register(client, users[2], ["treasure", "free"])
    tests.utils.web_dike_register(client, users[3], ["secret", "free"])
    tests.utils.web_dike_register(client, users[4], ["library", "free"])
    tests.utils.web_dike_register(client, users[5], ["free"])
    tests.utils.web_dike_register(client, users[6], ["free"])
    tests.utils.web_dike_register(client, users[7], ["free"])
    tests.utils.web_dike_register(client, users[8], ["covision"])
    tests.utils.web_dike_register(client, users[9], ["covision"])
    tests.utils.web_dike_register(client, users[10], ["covision"])

    tests.utils.web_dike_register(client, users[11], ["boss", "free"])

    tests.utils.web_dike_begin_voting(client)

    tests.utils.web_login(client, users[0])
    tests.utils.web_dike_ballot(client, [
        {"fellow": users[0], "position": "boss", "rank": 1},
        {"fellow": users[1], "position": "vice", "rank": 1},
        {"fellow": users[2], "position": "treasure", "rank": 1},
        {"fellow": users[3], "position": "secret", "rank": 1},
        {"fellow": users[4], "position": "library", "rank": 1},
        {"fellow": users[5], "position": "free", "rank": 1},
        {"fellow": users[6], "position": "free", "rank": 1},
        {"fellow": users[7], "position": "free", "rank": 1},
        {"fellow": users[8], "position": "covision", "rank": 1},
        {"fellow": users[9], "position": "covision", "rank": 1},
        {"fellow": users[10], "position": "covision", "rank": 1},

    ])

    tests.utils.web_login(client, users[1])
    tests.utils.web_dike_ballot(client, [
        {"fellow": users[0], "position": "boss", "rank": 1},
        {"fellow": users[11], "position": "boss", "rank": 2},
    ])

    tests.utils.web_login(client, blank_user)
    tests.utils.web_dike_end_voting(client)

    client.get("/dike/reckoning")

    tests.utils.web_dike_reckon(client, [
        {"position": "boss", "fellows": [users[11]]},
        {"position": "vice", "fellows": [users[1]]},
        {"position": "treasure", "fellows": [users[2]]},
        {"position": "secret", "fellows": [users[3]]},
        {"position": "library", "fellows": [users[4]]},
        {"position": "free", "fellows": [users[5], users[6], users[7]]},
        {"position": "covision", "fellows": [users[8], users[9], users[10]]},
    ])

    assert not users[11].check_board("boss")
    assert not users[11].check_board("board")

    assert not users[0].check_board("boss")
    assert not users[0].check_board("board")


def test_election_reckoning_multi_vice(client, blank_user, users):
    blank_user.set_board("board", True)

    tests.utils.web_login(client, blank_user)

    tests.utils.web_dike_begin_election(client)

    tests.utils.web_dike_register(client, users[0], ["boss", "free"])
    tests.utils.web_dike_register(client, users[1], ["vice", "free"])
    tests.utils.web_dike_register(client, users[2], ["treasure", "free"])
    tests.utils.web_dike_register(client, users[3], ["secret", "free"])
    tests.utils.web_dike_register(client, users[4], ["library", "free"])
    tests.utils.web_dike_register(client, users[5], ["free"])
    tests.utils.web_dike_register(client, users[6], ["free"])
    tests.utils.web_dike_register(client, users[7], ["free"])
    tests.utils.web_dike_register(client, users[8], ["covision"])
    tests.utils.web_dike_register(client, users[9], ["covision"])
    tests.utils.web_dike_register(client, users[10], ["covision"])

    tests.utils.web_dike_register(client, users[11], ["vice", "free"])

    tests.utils.web_dike_begin_voting(client)

    tests.utils.web_login(client, users[0])
    tests.utils.web_dike_ballot(client, [
        {"fellow": users[0], "position": "boss", "rank": 1},
        {"fellow": users[1], "position": "vice", "rank": 1},
        {"fellow": users[2], "position": "treasure", "rank": 1},
        {"fellow": users[3], "position": "secret", "rank": 1},
        {"fellow": users[4], "position": "library", "rank": 1},
        {"fellow": users[5], "position": "free", "rank": 1},
        {"fellow": users[6], "position": "free", "rank": 1},
        {"fellow": users[7], "position": "free", "rank": 1},
        {"fellow": users[8], "position": "covision", "rank": 1},
        {"fellow": users[9], "position": "covision", "rank": 1},
        {"fellow": users[10], "position": "covision", "rank": 1},

    ])

    tests.utils.web_login(client, users[1])
    tests.utils.web_dike_ballot(client, [
        {"fellow": users[11], "position": "vice", "rank": 1},
    ])

    tests.utils.web_login(client, blank_user)
    tests.utils.web_dike_end_voting(client)

    client.get("/dike/reckoning")

    tests.utils.web_dike_reckon(client, [
        {"position": "boss", "fellows": [users[0]]},
        {"position": "vice", "fellows": [users[1], users[11]]},
        {"position": "treasure", "fellows": [users[2]]},
        {"position": "secret", "fellows": [users[3]]},
        {"position": "library", "fellows": [users[4]]},
        {"position": "free", "fellows": [users[5], users[6], users[7]]},
        {"position": "covision", "fellows": [users[8], users[9], users[10]]},
    ])

    assert not users[11].check_board("vice")
    assert not users[11].check_board("board")

    assert not users[0].check_board("boss")
    assert not users[0].check_board("board")


def test_election_reckoning_too_many_free(client, blank_user, users):
    blank_user.set_board("board", True)

    tests.utils.web_login(client, blank_user)

    tests.utils.web_dike_begin_election(client)

    tests.utils.web_dike_register(client, users[0], ["boss", "free"])
    tests.utils.web_dike_register(client, users[1], ["vice", "free"])
    tests.utils.web_dike_register(client, users[2], ["treasure", "free"])
    tests.utils.web_dike_register(client, users[3], ["secret", "free"])
    tests.utils.web_dike_register(client, users[4], ["library", "free"])
    tests.utils.web_dike_register(client, users[5], ["free"])
    tests.utils.web_dike_register(client, users[6], ["free"])
    tests.utils.web_dike_register(client, users[7], ["free"])
    tests.utils.web_dike_register(client, users[8], ["covision"])
    tests.utils.web_dike_register(client, users[9], ["covision"])
    tests.utils.web_dike_register(client, users[10], ["covision"])

    tests.utils.web_dike_register(client, users[11], ["free"])

    tests.utils.web_dike_begin_voting(client)

    tests.utils.web_login(client, users[0])
    tests.utils.web_dike_ballot(client, [
        {"fellow": users[0], "position": "boss", "rank": 1},
        {"fellow": users[1], "position": "vice", "rank": 1},
        {"fellow": users[2], "position": "treasure", "rank": 1},
        {"fellow": users[3], "position": "secret", "rank": 1},
        {"fellow": users[4], "position": "library", "rank": 1},
        {"fellow": users[5], "position": "free", "rank": 1},
        {"fellow": users[6], "position": "free", "rank": 1},
        {"fellow": users[7], "position": "free", "rank": 1},
        {"fellow": users[8], "position": "covision", "rank": 1},
        {"fellow": users[9], "position": "covision", "rank": 1},
        {"fellow": users[10], "position": "covision", "rank": 1},

    ])

    tests.utils.web_login(client, users[1])
    tests.utils.web_dike_ballot(client, [
        {"fellow": users[11], "position": "free", "rank": 1},
    ])

    tests.utils.web_login(client, blank_user)
    tests.utils.web_dike_end_voting(client)

    client.get("/dike/reckoning")

    tests.utils.web_dike_reckon(client, [
        {"position": "boss", "fellows": [users[0]]},
        {"position": "vice", "fellows": [users[1]]},
        {"position": "treasure", "fellows": [users[2]]},
        {"position": "secret", "fellows": [users[3]]},
        {"position": "library", "fellows": [users[4]]},
        {"position": "free", "fellows": [users[5], users[6], users[7], users[11]]},
        {"position": "covision", "fellows": [users[8], users[9], users[10]]},
    ])

    assert not users[11].check_board("free")
    assert not users[11].check_board("board")

    assert not users[0].check_board("boss")
    assert not users[0].check_board("board")
