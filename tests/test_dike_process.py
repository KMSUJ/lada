import lada.models
import logging
import re
import tests.utils

from lada.dike import maintenance
from lada.constants import *
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

    tests.utils.web_dike_register(client, users[0], [POSITION_BOSS, POSITION_VICE, POSITION_FREE])
    tests.utils.web_dike_register(client, users[1], [POSITION_BOSS, POSITION_TREASURE, POSITION_LIBRARY, POSITION_FREE])
    tests.utils.web_dike_register(client, users[2], [POSITION_COVISION])

    election = maintenance.get_election()
    assert set(election.positions.filter_by(name=POSITION_BOSS).first().candidates.all()) == {users[0], users[1]}
    assert set(election.positions.filter_by(name=POSITION_VICE).first().candidates.all()) == {users[0]}
    assert set(election.positions.filter_by(name=POSITION_TREASURE).first().candidates.all()) == {users[1]}
    assert set(election.positions.filter_by(name=POSITION_SECRET).first().candidates.all()) == set()
    assert set(election.positions.filter_by(name=POSITION_LIBRARY).first().candidates.all()) == {users[1]}
    assert set(election.positions.filter_by(name=POSITION_FREE).first().candidates.all()) == {users[0], users[1]}
    assert set(election.positions.filter_by(name=POSITION_COVISION).first().candidates.all()) == {users[2]}


def test_register_candidates_without_free(client, blank_user, users):
    blank_user.set_board("board", True)

    tests.utils.web_login(client, blank_user)

    maintenance.begin_election()

    tests.utils.web_dike_register(client, users[0], [POSITION_BOSS, POSITION_VICE, POSITION_FREE])
    tests.utils.web_dike_register(client, users[1], [POSITION_BOSS, POSITION_VICE])

    election = maintenance.get_election()
    assert set(election.positions.filter_by(name=POSITION_BOSS).first().candidates.all()) == {users[0]}


def test_register_candidates_board_covision_conflict(client, blank_user, users):
    blank_user.set_board("board", True)

    tests.utils.web_login(client, blank_user)

    maintenance.begin_election()

    tests.utils.web_dike_register(client, users[0], [POSITION_BOSS, POSITION_FREE])
    tests.utils.web_dike_register(client, users[1], [POSITION_BOSS, POSITION_FREE, POSITION_COVISION])

    election = maintenance.get_election()
    assert set(election.positions.filter_by(name=POSITION_BOSS).first().candidates.all()) == {users[0]}


def test_register_candidates_board_positions_number_exceeded(client, blank_user, users):
    blank_user.set_board("board", True)

    tests.utils.web_login(client, blank_user)

    maintenance.begin_election()

    tests.utils.web_dike_register(client, users[0], [POSITION_BOSS, POSITION_VICE, POSITION_TREASURE, POSITION_FREE])
    tests.utils.web_dike_register(client, users[1], [POSITION_BOSS, POSITION_VICE, POSITION_TREASURE, POSITION_SECRET, POSITION_FREE])

    election = maintenance.get_election()
    assert set(election.positions.filter_by(name=POSITION_BOSS).first().candidates.all()) == {users[0]}


def test_register_candidates_multi_registration(client, blank_user, users):
    blank_user.set_board("board", True)

    tests.utils.web_login(client, blank_user)

    maintenance.begin_election()

    tests.utils.web_dike_register(client, users[0], [POSITION_BOSS, POSITION_FREE])
    tests.utils.web_dike_register(client, users[0], [POSITION_VICE, POSITION_FREE])

    election = maintenance.get_election()
    assert set(election.positions.filter_by(name=POSITION_BOSS).first().candidates.all()) == {users[0]}
    assert set(election.positions.filter_by(name=POSITION_VICE).first().candidates.all()) == set()
    assert set(election.positions.filter_by(name=POSITION_FREE).first().candidates.all()) == {users[0]}


def test_election_determinism(client, blank_user, users):
    blank_user.set_board("board", True)

    tests.utils.web_login(client, blank_user)

    tests.utils.web_dike_begin_election(client)

    tests.utils.web_dike_register(client, users[0], [POSITION_BOSS, POSITION_FREE])
    tests.utils.web_dike_register(client, users[1], [POSITION_BOSS, POSITION_FREE])

    tests.utils.web_dike_begin_voting(client)

    tests.utils.web_login(client, users[0])
    tests.utils.web_dike_ballot(client, [
        {
            "fellow": users[0],
            "position": POSITION_BOSS,
            "rank": 1,
        },
    ])

    tests.utils.web_login(client, users[1])
    tests.utils.web_dike_ballot(client, [
        {
            "fellow": users[1],
            "position": POSITION_BOSS,
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

    tests.utils.web_dike_register(client, users[0], [POSITION_BOSS, POSITION_FREE])
    tests.utils.web_dike_register(client, users[1], [POSITION_BOSS, POSITION_FREE])

    tests.utils.web_dike_begin_voting(client)

    assert len(lada.models.Vote.query.all()) == 0

    tests.utils.web_login(client, users[0])
    tests.utils.web_dike_ballot(client, [
        {
            "fellow": users[0],
            "position": POSITION_BOSS,
            "rank": 1,
        },
        {
            "fellow": users[1],
            "position": POSITION_BOSS,
            "rank": 1,
        },
    ])

    assert len(lada.models.Vote.query.all()) == 0


def test_election_missing_unvoted_candidate(client, blank_user, users):
    blank_user.set_board("board", True)

    tests.utils.web_login(client, blank_user)

    tests.utils.web_dike_begin_election(client)

    tests.utils.web_dike_register(client, users[0], [POSITION_BOSS, POSITION_FREE])
    tests.utils.web_dike_register(client, users[1], [POSITION_BOSS, POSITION_FREE])

    tests.utils.web_dike_begin_voting(client)

    tests.utils.web_login(client, users[0])
    tests.utils.web_dike_ballot(client, [
        {
            "fellow": users[0],
            "position": POSITION_BOSS,
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

    tests.utils.web_dike_register(client, users[0], [POSITION_BOSS, POSITION_FREE])

    tests.utils.web_dike_begin_voting(client)

    tests.utils.web_login(client, users[0])
    tests.utils.web_dike_ballot(client, [
        {
            "fellow": users[0],
            "position": POSITION_BOSS,
            "rank": 1,
        },
    ])

    tests.utils.web_login(client, users[1])
    tests.utils.web_dike_ballot(client, [
        {
            "fellow": users[1],
            "position": POSITION_BOSS,
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

    tests.utils.web_dike_register(client, users[0], [POSITION_BOSS, POSITION_FREE])
    tests.utils.web_dike_register(client, users[1], [POSITION_VICE, POSITION_FREE])
    tests.utils.web_dike_register(client, users[2], [POSITION_TREASURE, POSITION_FREE])
    tests.utils.web_dike_register(client, users[3], [POSITION_SECRET, POSITION_FREE])
    tests.utils.web_dike_register(client, users[4], [POSITION_LIBRARY, POSITION_FREE])
    tests.utils.web_dike_register(client, users[5], [POSITION_FREE])
    tests.utils.web_dike_register(client, users[6], [POSITION_FREE])
    tests.utils.web_dike_register(client, users[7], [POSITION_FREE])
    tests.utils.web_dike_register(client, users[8], [POSITION_COVISION])
    tests.utils.web_dike_register(client, users[9], [POSITION_COVISION])
    tests.utils.web_dike_register(client, users[10], [POSITION_COVISION])

    tests.utils.web_dike_register(client, users[11], [POSITION_VICE, POSITION_FREE])
    tests.utils.web_dike_register(client, users[12], [POSITION_TREASURE, POSITION_FREE])

    tests.utils.web_dike_begin_voting(client)

    tests.utils.web_login(client, users[0])
    tests.utils.web_dike_ballot(client, [
        {"fellow": users[0], "position": POSITION_BOSS, "rank": 1},
        {"fellow": users[1], "position": POSITION_VICE, "rank": 1},
        {"fellow": users[2], "position": POSITION_TREASURE, "rank": 1},
        {"fellow": users[3], "position": POSITION_SECRET, "rank": 1},
        {"fellow": users[4], "position": POSITION_LIBRARY, "rank": 1},
        {"fellow": users[5], "position": POSITION_FREE, "rank": 1},
        {"fellow": users[6], "position": POSITION_FREE, "rank": 2},
        {"fellow": users[7], "position": POSITION_FREE, "rank": 3},
        {"fellow": users[8], "position": POSITION_COVISION, "rank": 1},
        {"fellow": users[9], "position": POSITION_COVISION, "rank": 2},
        {"fellow": users[10], "position": POSITION_COVISION, "rank": 3},

    ])

    tests.utils.web_login(client, users[1])
    tests.utils.web_dike_ballot(client, [
        {"fellow": users[11], "position": POSITION_VICE, "rank": 1},
        {"fellow": users[12], "position": POSITION_TREASURE, "rank": 1},
    ])

    tests.utils.web_login(client, blank_user)
    tests.utils.web_dike_end_voting(client)

    client.get("/dike/reckoning")

    election = maintenance.get_election()
    positions = election.positions.all()
    for position in positions:
        assert position.is_reckoned

    tests.utils.web_dike_reckon(client, [
        {"position": POSITION_BOSS, "fellows": [users[0]]},
        {"position": POSITION_VICE, "fellows": [users[11]]},
        {"position": POSITION_TREASURE, "fellows": [users[2]]},
        {"position": POSITION_SECRET, "fellows": [users[3]]},
        {"position": POSITION_LIBRARY, "fellows": [users[4]]},
        {"position": POSITION_FREE, "fellows": [users[1], users[6], users[7]]},
        {"position": POSITION_COVISION, "fellows": [users[8], users[9], users[10]]},
    ])

    assert users[0].check_board(POSITION_BOSS)
    assert users[0].check_board("board")
    assert users[11].check_board(POSITION_VICE)
    assert users[11].check_board("board")
    assert users[2].check_board(POSITION_TREASURE)
    assert users[2].check_board("board")
    assert users[3].check_board(POSITION_SECRET)
    assert users[3].check_board("board")
    assert users[4].check_board(POSITION_LIBRARY)
    assert users[4].check_board("board")
    assert users[1].check_board(POSITION_FREE)
    assert users[1].check_board("board")
    assert users[6].check_board(POSITION_FREE)
    assert users[6].check_board("board")
    assert users[7].check_board(POSITION_FREE)
    assert users[7].check_board("board")
    assert users[8].check_board(POSITION_COVISION)
    assert users[9].check_board(POSITION_COVISION)
    assert users[10].check_board(POSITION_COVISION)

    assert not users[12].check_board(POSITION_TREASURE)
    assert not users[12].check_board("board")


def test_election_reckoning_candidate_injection(client, blank_user, users):
    blank_user.set_board("board", True)

    tests.utils.web_login(client, blank_user)

    tests.utils.web_dike_begin_election(client)

    tests.utils.web_dike_register(client, users[0], [POSITION_BOSS, POSITION_FREE])
    tests.utils.web_dike_register(client, users[1], [POSITION_VICE, POSITION_FREE])
    tests.utils.web_dike_register(client, users[2], [POSITION_TREASURE, POSITION_FREE])
    tests.utils.web_dike_register(client, users[3], [POSITION_SECRET, POSITION_FREE])
    tests.utils.web_dike_register(client, users[4], [POSITION_LIBRARY, POSITION_FREE])
    tests.utils.web_dike_register(client, users[5], [POSITION_FREE])
    tests.utils.web_dike_register(client, users[6], [POSITION_FREE])
    tests.utils.web_dike_register(client, users[7], [POSITION_FREE])
    tests.utils.web_dike_register(client, users[8], [POSITION_COVISION])
    tests.utils.web_dike_register(client, users[9], [POSITION_COVISION])
    tests.utils.web_dike_register(client, users[10], [POSITION_COVISION])

    tests.utils.web_dike_begin_voting(client)

    tests.utils.web_login(client, users[0])
    tests.utils.web_dike_ballot(client, [
        {"fellow": users[0], "position": POSITION_BOSS, "rank": 1},
        {"fellow": users[1], "position": POSITION_VICE, "rank": 1},
        {"fellow": users[2], "position": POSITION_TREASURE, "rank": 1},
        {"fellow": users[3], "position": POSITION_SECRET, "rank": 1},
        {"fellow": users[4], "position": POSITION_LIBRARY, "rank": 1},
        {"fellow": users[5], "position": POSITION_FREE, "rank": 1},
        {"fellow": users[6], "position": POSITION_FREE, "rank": 1},
        {"fellow": users[7], "position": POSITION_FREE, "rank": 1},
        {"fellow": users[8], "position": POSITION_COVISION, "rank": 1},
        {"fellow": users[9], "position": POSITION_COVISION, "rank": 1},
        {"fellow": users[10], "position": POSITION_COVISION, "rank": 1},

    ])

    tests.utils.web_login(client, blank_user)
    tests.utils.web_dike_end_voting(client)

    client.get("/dike/reckoning")

    tests.utils.web_dike_reckon(client, [
        {"position": POSITION_BOSS, "fellows": [users[0]]},
        {"position": POSITION_VICE, "fellows": [users[11]]},  # injection
        {"position": POSITION_TREASURE, "fellows": [users[2]]},
        {"position": POSITION_SECRET, "fellows": [users[3]]},
        {"position": POSITION_LIBRARY, "fellows": [users[4]]},
        {"position": POSITION_FREE, "fellows": [users[5], users[6], users[7]]},
        {"position": POSITION_COVISION, "fellows": [users[8], users[9], users[10]]},
    ])

    assert not users[11].check_board(POSITION_VICE)
    assert not users[11].check_board("board")

    assert not users[0].check_board(POSITION_BOSS)
    assert not users[0].check_board("board")


def test_election_reckoning_candidate_boss_change(client, blank_user, users):
    blank_user.set_board("board", True)

    tests.utils.web_login(client, blank_user)

    tests.utils.web_dike_begin_election(client)

    tests.utils.web_dike_register(client, users[0], [POSITION_BOSS, POSITION_FREE])
    tests.utils.web_dike_register(client, users[1], [POSITION_VICE, POSITION_FREE])
    tests.utils.web_dike_register(client, users[2], [POSITION_TREASURE, POSITION_FREE])
    tests.utils.web_dike_register(client, users[3], [POSITION_SECRET, POSITION_FREE])
    tests.utils.web_dike_register(client, users[4], [POSITION_LIBRARY, POSITION_FREE])
    tests.utils.web_dike_register(client, users[5], [POSITION_FREE])
    tests.utils.web_dike_register(client, users[6], [POSITION_FREE])
    tests.utils.web_dike_register(client, users[7], [POSITION_FREE])
    tests.utils.web_dike_register(client, users[8], [POSITION_COVISION])
    tests.utils.web_dike_register(client, users[9], [POSITION_COVISION])
    tests.utils.web_dike_register(client, users[10], [POSITION_COVISION])

    tests.utils.web_dike_register(client, users[11], [POSITION_BOSS, POSITION_FREE])

    tests.utils.web_dike_begin_voting(client)

    tests.utils.web_login(client, users[0])
    tests.utils.web_dike_ballot(client, [
        {"fellow": users[0], "position": POSITION_BOSS, "rank": 1},
        {"fellow": users[1], "position": POSITION_VICE, "rank": 1},
        {"fellow": users[2], "position": POSITION_TREASURE, "rank": 1},
        {"fellow": users[3], "position": POSITION_SECRET, "rank": 1},
        {"fellow": users[4], "position": POSITION_LIBRARY, "rank": 1},
        {"fellow": users[5], "position": POSITION_FREE, "rank": 1},
        {"fellow": users[6], "position": POSITION_FREE, "rank": 1},
        {"fellow": users[7], "position": POSITION_FREE, "rank": 1},
        {"fellow": users[8], "position": POSITION_COVISION, "rank": 1},
        {"fellow": users[9], "position": POSITION_COVISION, "rank": 1},
        {"fellow": users[10], "position": POSITION_COVISION, "rank": 1},

    ])

    tests.utils.web_login(client, users[1])
    tests.utils.web_dike_ballot(client, [
        {"fellow": users[0], "position": POSITION_BOSS, "rank": 1},
        {"fellow": users[11], "position": POSITION_BOSS, "rank": 2},
    ])

    tests.utils.web_login(client, blank_user)
    tests.utils.web_dike_end_voting(client)

    client.get("/dike/reckoning")

    tests.utils.web_dike_reckon(client, [
        {"position": POSITION_BOSS, "fellows": [users[11]]},
        {"position": POSITION_VICE, "fellows": [users[1]]},
        {"position": POSITION_TREASURE, "fellows": [users[2]]},
        {"position": POSITION_SECRET, "fellows": [users[3]]},
        {"position": POSITION_LIBRARY, "fellows": [users[4]]},
        {"position": POSITION_FREE, "fellows": [users[5], users[6], users[7]]},
        {"position": POSITION_COVISION, "fellows": [users[8], users[9], users[10]]},
    ])

    assert not users[11].check_board(POSITION_BOSS)
    assert not users[11].check_board("board")

    assert not users[0].check_board(POSITION_BOSS)
    assert not users[0].check_board("board")


def test_election_reckoning_multi_vice(client, blank_user, users):
    blank_user.set_board("board", True)

    tests.utils.web_login(client, blank_user)

    tests.utils.web_dike_begin_election(client)

    tests.utils.web_dike_register(client, users[0], [POSITION_BOSS, POSITION_FREE])
    tests.utils.web_dike_register(client, users[1], [POSITION_VICE, POSITION_FREE])
    tests.utils.web_dike_register(client, users[2], [POSITION_TREASURE, POSITION_FREE])
    tests.utils.web_dike_register(client, users[3], [POSITION_SECRET, POSITION_FREE])
    tests.utils.web_dike_register(client, users[4], [POSITION_LIBRARY, POSITION_FREE])
    tests.utils.web_dike_register(client, users[5], [POSITION_FREE])
    tests.utils.web_dike_register(client, users[6], [POSITION_FREE])
    tests.utils.web_dike_register(client, users[7], [POSITION_FREE])
    tests.utils.web_dike_register(client, users[8], [POSITION_COVISION])
    tests.utils.web_dike_register(client, users[9], [POSITION_COVISION])
    tests.utils.web_dike_register(client, users[10], [POSITION_COVISION])

    tests.utils.web_dike_register(client, users[11], [POSITION_VICE, POSITION_FREE])

    tests.utils.web_dike_begin_voting(client)

    tests.utils.web_login(client, users[0])
    tests.utils.web_dike_ballot(client, [
        {"fellow": users[0], "position": POSITION_BOSS, "rank": 1},
        {"fellow": users[1], "position": POSITION_VICE, "rank": 1},
        {"fellow": users[2], "position": POSITION_TREASURE, "rank": 1},
        {"fellow": users[3], "position": POSITION_SECRET, "rank": 1},
        {"fellow": users[4], "position": POSITION_LIBRARY, "rank": 1},
        {"fellow": users[5], "position": POSITION_FREE, "rank": 1},
        {"fellow": users[6], "position": POSITION_FREE, "rank": 1},
        {"fellow": users[7], "position": POSITION_FREE, "rank": 1},
        {"fellow": users[8], "position": POSITION_COVISION, "rank": 1},
        {"fellow": users[9], "position": POSITION_COVISION, "rank": 1},
        {"fellow": users[10], "position": POSITION_COVISION, "rank": 1},

    ])

    tests.utils.web_login(client, users[1])
    tests.utils.web_dike_ballot(client, [
        {"fellow": users[11], "position": POSITION_VICE, "rank": 1},
    ])

    tests.utils.web_login(client, blank_user)
    tests.utils.web_dike_end_voting(client)

    client.get("/dike/reckoning")

    tests.utils.web_dike_reckon(client, [
        {"position": POSITION_BOSS, "fellows": [users[0]]},
        {"position": POSITION_VICE, "fellows": [users[1], users[11]]},
        {"position": POSITION_TREASURE, "fellows": [users[2]]},
        {"position": POSITION_SECRET, "fellows": [users[3]]},
        {"position": POSITION_LIBRARY, "fellows": [users[4]]},
        {"position": POSITION_FREE, "fellows": [users[5], users[6], users[7]]},
        {"position": POSITION_COVISION, "fellows": [users[8], users[9], users[10]]},
    ])

    assert not users[11].check_board(POSITION_VICE)
    assert not users[11].check_board("board")

    assert not users[0].check_board(POSITION_BOSS)
    assert not users[0].check_board("board")


def test_election_reckoning_too_many_free(client, blank_user, users):
    blank_user.set_board("board", True)

    tests.utils.web_login(client, blank_user)

    tests.utils.web_dike_begin_election(client)

    tests.utils.web_dike_register(client, users[0], [POSITION_BOSS, POSITION_FREE])
    tests.utils.web_dike_register(client, users[1], [POSITION_VICE, POSITION_FREE])
    tests.utils.web_dike_register(client, users[2], [POSITION_TREASURE, POSITION_FREE])
    tests.utils.web_dike_register(client, users[3], [POSITION_SECRET, POSITION_FREE])
    tests.utils.web_dike_register(client, users[4], [POSITION_LIBRARY, POSITION_FREE])
    tests.utils.web_dike_register(client, users[5], [POSITION_FREE])
    tests.utils.web_dike_register(client, users[6], [POSITION_FREE])
    tests.utils.web_dike_register(client, users[7], [POSITION_FREE])
    tests.utils.web_dike_register(client, users[8], [POSITION_COVISION])
    tests.utils.web_dike_register(client, users[9], [POSITION_COVISION])
    tests.utils.web_dike_register(client, users[10], [POSITION_COVISION])

    tests.utils.web_dike_register(client, users[11], [POSITION_FREE])

    tests.utils.web_dike_begin_voting(client)

    tests.utils.web_login(client, users[0])
    tests.utils.web_dike_ballot(client, [
        {"fellow": users[0], "position": POSITION_BOSS, "rank": 1},
        {"fellow": users[1], "position": POSITION_VICE, "rank": 1},
        {"fellow": users[2], "position": POSITION_TREASURE, "rank": 1},
        {"fellow": users[3], "position": POSITION_SECRET, "rank": 1},
        {"fellow": users[4], "position": POSITION_LIBRARY, "rank": 1},
        {"fellow": users[5], "position": POSITION_FREE, "rank": 1},
        {"fellow": users[6], "position": POSITION_FREE, "rank": 1},
        {"fellow": users[7], "position": POSITION_FREE, "rank": 1},
        {"fellow": users[8], "position": POSITION_COVISION, "rank": 1},
        {"fellow": users[9], "position": POSITION_COVISION, "rank": 1},
        {"fellow": users[10], "position": POSITION_COVISION, "rank": 1},

    ])

    tests.utils.web_login(client, users[1])
    tests.utils.web_dike_ballot(client, [
        {"fellow": users[11], "position": POSITION_FREE, "rank": 1},
    ])

    tests.utils.web_login(client, blank_user)
    tests.utils.web_dike_end_voting(client)

    client.get("/dike/reckoning")

    tests.utils.web_dike_reckon(client, [
        {"position": POSITION_BOSS, "fellows": [users[0]]},
        {"position": POSITION_VICE, "fellows": [users[1]]},
        {"position": POSITION_TREASURE, "fellows": [users[2]]},
        {"position": POSITION_SECRET, "fellows": [users[3]]},
        {"position": POSITION_LIBRARY, "fellows": [users[4]]},
        {"position": POSITION_FREE, "fellows": [users[5], users[6], users[7], users[11]]},
        {"position": POSITION_COVISION, "fellows": [users[8], users[9], users[10]]},
    ])

    assert not users[11].check_board(POSITION_FREE)
    assert not users[11].check_board("board")

    assert not users[0].check_board(POSITION_BOSS)
    assert not users[0].check_board("board")
