import unittest

from lada.dike.stv.ballot import Ballot
from lada.dike.stv.candidate import Candidate
from lada.dike.stv.tally import Tally


class TestDikeSTV(unittest.TestCase):
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
