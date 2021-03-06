from pytest import raises

from lada.dike.maintenance import ArbitraryDiscardDecisionNeededError
from lada.dike.stv.ballot import Ballot
from lada.dike.stv.candidate import Candidate
from lada.dike.stv.tally import Tally
from tests.fixtures import *


def test_ballot_active(app):
    c = [
        Candidate("C0"),
        Candidate("C1"),
    ]

    ballot = Ballot(preference=[c[0], c[1]])
    ballot.check_active()

    assert ballot.value == 1


def test_ballot_inactive(app):
    ballot = Ballot(preference=[])
    ballot.check_active()

    assert ballot.value == 0


def test_ballot_preference_reject_conflict(app, feature_flags):
    feature_flags.enable(FEATURE_STV_REJECTION)

    c = [
        Candidate("C0"),
        Candidate("C1"),
        Candidate("C2"),
    ]

    with pytest.raises(ValueError):
        Ballot(preference=[c[0], c[1]], reject=[c[0], c[2]])


def test_ballot_preference_duplicate(app):
    c = [
        Candidate("C0"),
        Candidate("C1"),
    ]

    with pytest.raises(ValueError):
        Ballot(preference=[c[0], c[1], c[0]])


def test_ballot_preference_nontrivial_duplicate(app):
    c = [
        Candidate("C0"),
        Candidate("C0"),
    ]

    with pytest.raises(ValueError):
        Ballot(preference=[c[0], c[1]])


def test_tally_with_single_ballot(app):
    c = [
        Candidate("C0"),
        Candidate("C1"),
        Candidate("C2"),
    ]

    ballots = [
        Ballot(preference=[c[0], c[1], c[2]]),
    ]

    tally = Tally(ballots=ballots)

    elected, discarded, rejected = tally.run()

    assert set(elected) == {c[0]}
    assert set(discarded) == {c[1], c[2]}
    assert set(rejected) == set()


def test_tally_simple_run_001(app):
    c = [
        Candidate("C0"),
        Candidate("C1"),
        Candidate("C2"),
    ]

    ballots = [
        Ballot(preference=[c[0], c[2]]),
        Ballot(preference=[c[0], c[1]]),
        Ballot(preference=[c[2], c[1]]),
    ]

    tally = Tally(ballots=ballots)

    elected, discarded, rejected = tally.run()

    assert set(elected) == {c[0]}
    assert set(discarded) == {c[1], c[2]}
    assert set(rejected) == set()


def test_tally_simple_run_002(app):
    c = [
        Candidate("C0"),
        Candidate("C1"),
        Candidate("C2"),
    ]

    ballots = [
        Ballot(preference=[c[0]]),
        Ballot(preference=[c[0]]),
        Ballot(preference=[c[1]]),
    ]

    tally = Tally(ballots=ballots)

    elected, discarded, rejected = tally.run()

    assert set(elected) == {c[0]}
    assert set(discarded) == {c[1]}
    assert set(rejected) == set()


def test_tally_single_ballot_with_rejection(app, feature_flags):
    feature_flags.enable(FEATURE_STV_REJECTION)

    c = [
        Candidate("C0"),
        Candidate("C1"),
    ]

    ballots = [
        Ballot(preference=[c[0]], reject=[c[1]]),
    ]

    tally = Tally(ballots=ballots)

    elected, discarded, rejected = tally.run()

    assert set(elected) == {c[0]}
    assert set(discarded) == set()
    assert set(rejected) == {c[1]}


def test_tally_with_simple_mutual_rejection(app, feature_flags):
    feature_flags.enable(FEATURE_STV_REJECTION)

    c = [
        Candidate("C0"),
        Candidate("C1"),
    ]

    ballots = [
        Ballot(preference=[c[0]], reject=[c[1]]),
        Ballot(preference=[c[1]], reject=[c[0]]),
    ]

    tally = Tally(ballots=ballots)

    elected, discarded, rejected = tally.run()

    assert set(elected) == set()
    assert set(discarded) == set()
    assert set(rejected) == {c[0], c[1]}


def test_tally_with_mutual_rejection_paradox(app, feature_flags):
    feature_flags.enable(FEATURE_STV_REJECTION)

    c = [
        Candidate("C0"),
        Candidate("C1"),
        Candidate("C2"),
    ]

    ballots = [
        Ballot(preference=[c[0]], reject=[c[1]]),
        Ballot(preference=[c[0]], reject=[c[1]]),
        Ballot(preference=[c[0]], reject=[c[1]]),
        Ballot(preference=[c[1]], reject=[c[0]]),
        Ballot(preference=[c[1]], reject=[c[0]]),
        Ballot(preference=[c[1]], reject=[c[0]]),
        Ballot(preference=[c[0], c[1], c[2]]),
    ]

    tally = Tally(ballots=ballots)

    elected, discarded, rejected = tally.run()

    assert set(elected) == {c[2]}
    assert set(discarded) == set()
    assert set(rejected) == {c[0], c[1]}


def test_multi_vacancy_tally_with_single_ballot(app):
    c = [
        Candidate("C0"),
        Candidate("C1"),
        Candidate("C2"),
        Candidate("C3"),
        Candidate("C4"),
    ]

    ballots = [
        Ballot(preference=[c[3], c[1], c[4], c[2], c[0]]),
    ]

    tally = Tally(ballots=ballots, vacancies=3)

    elected, discarded, rejected = tally.run()

    assert set(elected) == {c[1], c[3], c[4]}
    assert set(discarded) == {c[0], c[2]}
    assert set(rejected) == set()


def test_vote_transfer_scenario(app):
    c = [
        Candidate("C0"),
        Candidate("C1"),
        Candidate("C2"),
        Candidate("C3"),
    ]

    ballots = [
        Ballot(preference=[c[0]]),
        Ballot(preference=[c[0]]),
        Ballot(preference=[c[0], c[3]]),
        Ballot(preference=[c[1]]),
        Ballot(preference=[c[1]]),
        Ballot(preference=[c[2], c[1]]),
        Ballot(preference=[c[3], c[1]]),
    ]

    tally = Tally(ballots=ballots, vacancies=1)

    elected, discarded, rejected = tally.run()

    assert set(elected) == {c[1]}
    assert set(discarded) == {c[0], c[2], c[3]}
    assert set(rejected) == set()


def test_multi_vacancy_vote_transfer_scenario_not_enough(app):
    c = [
        Candidate("C0"),
        Candidate("C1"),
        Candidate("C2"),
        Candidate("C3"),
    ]

    ballots = [
        Ballot(preference=[c[0], c[2]]),
        Ballot(preference=[c[0], c[2]]),
        Ballot(preference=[c[0], c[2]]),
        Ballot(preference=[c[0], c[2]]),
        Ballot(preference=[c[0], c[3]]),
        Ballot(preference=[c[1]]),
        Ballot(preference=[c[1]]),
        Ballot(preference=[c[1]]),
        Ballot(preference=[c[2]]),
    ]

    tally = Tally(ballots=ballots, vacancies=2)

    elected, discarded, rejected = tally.run()

    assert set(elected) == {c[0], c[1]}
    assert set(discarded) == {c[2], c[3]}
    assert set(rejected) == set()


def test_multi_vacancy_vote_transfer_scenario_enough(app):
    c = [
        Candidate("C0"),
        Candidate("C1"),
        Candidate("C2"),
        Candidate("C3"),
    ]

    ballots = [
        Ballot(preference=[c[0], c[2]]),
        Ballot(preference=[c[0], c[2]]),
        Ballot(preference=[c[0], c[2]]),
        Ballot(preference=[c[0], c[2]]),
        Ballot(preference=[c[0], c[2]]),
        Ballot(preference=[c[0], c[3]]),
        Ballot(preference=[c[1]]),
        Ballot(preference=[c[1]]),
        Ballot(preference=[c[1]]),
        Ballot(preference=[c[2]]),
    ]

    tally = Tally(ballots=ballots, vacancies=2)

    elected, discarded, rejected = tally.run()

    assert set(elected) == {c[0], c[2]}
    assert set(discarded) == {c[1], c[3]}
    assert set(rejected) == set()


def test_arbitrary_decision_needed(app):
    c = [
        Candidate("C0"),
        Candidate("C1"),
        Candidate("C2"),
        Candidate("C3"),
    ]

    ballots = [
        Ballot(preference=[c[0]]),
        Ballot(preference=[c[1]]),
        Ballot(preference=[c[2]]),
        Ballot(preference=[c[3]]),
        Ballot(preference=[c[3]]),
    ]

    tally = Tally(ballots=ballots)

    with raises(ArbitraryDiscardDecisionNeededError):
        tally.run()


def test_arbitrary_decision_provided(app):
    c = [
        Candidate("C0"),
        Candidate("C1"),
        Candidate("C2"),
        Candidate("C3"),
    ]

    ballots = [
        Ballot(preference=[c[0]]),
        Ballot(preference=[c[1]]),
        Ballot(preference=[c[2]]),
        Ballot(preference=[c[3]]),
        Ballot(preference=[c[3]]),
    ]

    arbitrary_discards = [
        [c[0], c[1]],
    ]

    tally = Tally(ballots=ballots, arbitrary_discards=arbitrary_discards)

    elected, discarded, rejected = tally.run()

    assert set(elected) == {c[3]}
    assert set(discarded) == {c[0], c[1], c[2]}
    assert set(rejected) == set()


def test_single_candidate_with_zero_score(app):
    c = [
        Candidate("C0"),
    ]

    ballots = [
    ]

    tally = Tally(ballots=ballots, candidates=c)

    elected, discarded, rejected = tally.run()

    assert set(elected) == set()
    assert set(discarded) == {c[0]}
    assert set(rejected) == set()


def test_single_candidate_with_zero_score_2(app):
    c = [
        Candidate("C0"),
        Candidate("C1"),
    ]

    ballots = [
        Ballot(preference=[c[1]]),
    ]

    tally = Tally(ballots=ballots, candidates=c)

    elected, discarded, rejected = tally.run()

    assert set(elected) == {c[1]}
    assert set(discarded) == {c[0]}
    assert set(rejected) == set()


def test_single_candidate_with_zero_score_3(app):
    c = [
        Candidate("C0"),
        Candidate("C1"),
    ]

    ballots = [
        Ballot(preference=[c[1]]),
    ]

    tally = Tally(ballots=ballots, candidates=c, vacancies=2)

    elected, discarded, rejected = tally.run()

    assert set(elected) == {c[1]}
    assert set(discarded) == {c[0]}
    assert set(rejected) == set()
