import unittest

import lada

from lada.dike.stv.ballot import Ballot
from lada.dike.stv.candidate import Candidate
from lada.dike.stv.tally import Tally


class TestDikeSTV(unittest.TestCase):
  def setUp(self):
    self.feature_flags = []

    self.app = lada.create_app()
    self.ctx = self.app.app_context()
    self.ctx.push()

    lada.feature_flags.clear_handlers()
    lada.feature_flags.add_handler(self.feature_flags_handler)

  def tearDown(self):
    self.ctx.pop()
    lada.feature_flags.clear_handlers()

  def feature_flags_handler(self, flag):
    return flag in self.feature_flags

  def test_ballot_active(self):
    c = [
      Candidate("C0"),
      Candidate("C1"),
    ]

    ballot = Ballot(preference=[c[0], c[1]])
    ballot.check_active()

    self.assertEqual(1, ballot.value)

  def test_ballot_inactive(self):
    ballot = Ballot(preference=[])
    ballot.check_active()

    self.assertEqual(0, ballot.value)

  def test_ballot_preference_reject_conflict(self):
    self.feature_flags.append("stv_rejection")

    c = [
      Candidate("C0"),
      Candidate("C1"),
      Candidate("C2"),
    ]

    self.assertRaises(ValueError, Ballot, preference=[c[0], c[1]], reject=[c[0], c[2]])

  def test_ballot_preference_duplicate(self):
    c = [
      Candidate("C0"),
      Candidate("C1"),
    ]

    self.assertRaises(ValueError, Ballot, preference=[c[0], c[1], c[0]])

  def test_ballot_preference_nontrivial_duplicate(self):
    c = [
      Candidate("C0"),
      Candidate("C0"),
    ]

    self.assertRaises(ValueError, Ballot, preference=[c[0], c[1]])

  def test_tally_with_single_ballot(self):
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

    self.assertEqual({c[0]}, set(elected))
    self.assertEqual({c[1], c[2]}, set(discarded))
    self.assertEqual(set(), set(rejected))

  def test_tally_simple_run_001(self):
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

    self.assertEqual({c[0]}, set(elected))
    self.assertEqual({c[1], c[2]}, set(discarded))
    self.assertEqual(set(), set(rejected))

  def test_tally_simple_run_002(self):
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

    self.assertEqual({c[0]}, set(elected))
    self.assertEqual({c[1]}, set(discarded))
    self.assertEqual(set(), set(rejected))

  def test_tally_single_ballot_with_rejection(self):
    self.feature_flags.append("stv_rejection")

    c = [
      Candidate("C0"),
      Candidate("C1"),
    ]

    ballots = [
      Ballot(preference=[c[0]], reject=[c[1]]),
    ]

    tally = Tally(ballots=ballots)

    elected, discarded, rejected = tally.run()

    self.assertEqual({c[0]}, set(elected))
    self.assertEqual(set(), set(discarded))
    self.assertEqual({c[1]}, set(rejected))

  def test_tally_with_simple_mutual_rejection(self):
    self.feature_flags.append("stv_rejection")

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

    self.assertEqual(set(), set(elected))
    self.assertEqual(set(), set(discarded))
    self.assertEqual({c[0], c[1]}, set(rejected))

  def test_tally_with_mutual_rejection_paradox(self):
    self.feature_flags.append("stv_rejection")

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

    self.assertEqual({c[2]}, set(elected))
    self.assertEqual(set(), set(discarded))
    self.assertEqual({c[0], c[1]}, set(rejected))

  def test_tally_single_ballot_without_rejection(self):
    c = [
      Candidate("C0"),
      Candidate("C1"),
    ]

    ballots = [
      Ballot(preference=[c[0]], reject=[c[1]]),
    ]

    tally = Tally(ballots=ballots)

    elected, discarded, rejected = tally.run()

    self.assertEqual({c[0]}, set(elected))
    self.assertEqual({c[1]}, set(discarded))
    self.assertEqual(set(), set(rejected))

  def test_multi_vacancy_tally_with_single_ballot(self):
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

    self.assertEqual({c[1], c[3], c[4]}, set(elected))
    self.assertEqual({c[0], c[2]}, set(discarded))
    self.assertEqual(set(), set(rejected))

  def test_vote_transfer_scenario(self):
    c = [
      Candidate("C0"),
      Candidate("C1"),
      Candidate("C2"),
      Candidate("C3"),
    ]

    ballots = [
      Ballot(preference=[c[0]]),
      Ballot(preference=[c[0]]),
      Ballot(preference=[c[0]]),
      Ballot(preference=[c[1]]),
      Ballot(preference=[c[1]]),
      Ballot(preference=[c[2], c[1]]),
      Ballot(preference=[c[3], c[1]]),
    ]

    tally = Tally(ballots=ballots, vacancies=1)

    elected, discarded, rejected = tally.run()

    self.assertEqual({c[1]}, set(elected))
    self.assertEqual({c[0], c[2], c[3]}, set(discarded))
    self.assertEqual(set(), set(rejected))
    raise
