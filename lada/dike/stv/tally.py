import logging
from copy import copy
from operator import attrgetter

import flask_featureflags as feature

from lada.constants import FEATURE_STV_REJECTION


class Tally:
    def __init__(self, ballots, vacancies=1, candidates=None, arbitrary_discards=None):
        self.log = logging.getLogger(__name__)
        self.ballots = ballots
        self.vacancies = vacancies
        self.candidates = list(candidates or self.read_candidates())
        self.elected = list()
        self.discarded = list()
        self.rejected = set()
        self.results = dict()
        self.quota = self.evaluate_quota()

        self.arbitrary_discards_pointer = 0
        self.arbitrary_discards = arbitrary_discards or []

    def read_candidates(self):
        return list({candidate for ballot in self.ballots for candidate in set(ballot.preference) | ballot.reject})

    def evaluate_quota(self):
        return sum([ballot.value for ballot in self.ballots]) / (self.vacancies - len(self.elected) + 1)

    def reject_candidates(self, threshold=0.4):
        rejecting_count = threshold * len(self.ballots)
        self.log.info(f'Rejecting candidates. rejecting_count = {rejecting_count}')
        for candidate in copy(self.candidates):
            rejection_count = len([ballot for ballot in self.ballots if candidate in ballot.reject])
            self.log.debug(f'{candidate} rejection_count = {rejection_count}')
            if rejection_count > rejecting_count:
                self.log.info(f'Rejecting {candidate}')
                self.rejected.add(candidate)
                self.transfer_ballots(candidate)
                self.candidates.remove(candidate)

    def transfer_ballots(self, candidate, excess=0):
        self.log.debug(f'Transferring ballots with excess = {excess}')

        if excess > 0:
            candidate_score = candidate.score[-1][0]
            value_multiplier = excess / candidate_score
        else:
            value_multiplier = 1

        self.log.debug(f'value_multiplier = {value_multiplier}')

        for ballot in self.ballots:
            if candidate in ballot.preference:
                if ballot.first_preference() == candidate:
                    ballot.value *= value_multiplier
                ballot.discard(candidate)

    def elect(self, candidate):
        self.elected.append(candidate)
        self.log.info(f'Electing candidate {candidate} with score {candidate.score[-1][0]}')
        self.results.update({candidate:candidate.score[-1][0]})
        excess = candidate.score[-1][0] - self.quota
        self.transfer_ballots(candidate, excess)
        self.candidates.remove(candidate)

    def discard(self, candidate):
        self.discarded.append(candidate)
        self.log.info(f'Discarding candidate {candidate} with score {candidate.score[-1][0]}')
        self.results.update({candidate:candidate.score[-1][0]})
        self.transfer_ballots(candidate)
        self.candidates.remove(candidate)

    def count_votes(self):
        counter = {candidate: [0 for candidate in self.candidates] for candidate in self.candidates}
        for ballot in self.ballots:
            if ballot.value > 0:
                for j in range(len(ballot.preference)):
                    counter[ballot.preference[j]][j] += ballot.value
        return counter
    
    def score_votes(self, votes):
        for candidate in votes:
            candidate.score.append(votes[candidate])

    def round(self):
        self.log.info(f'Starting new round')
        self.log.debug(f'candidates = {sorted(self.candidates, key=attrgetter("id"))}')
        self.log.debug(f'elected = {sorted(self.elected, key=attrgetter("id"))}')
        self.log.debug(f'discarded = {sorted(self.discarded, key=attrgetter("id"))}')
        self.log.debug(f'rejected = {sorted(self.rejected, key=attrgetter("id"))}')
        counted_votes = self.count_votes()
        self.log.debug(f'counted_votes = {sorted(counted_votes.items(), key=lambda k: k[0].id)}')
        self.score_votes(counted_votes)
        self.candidates.sort()
        self.log.debug(f'sorted_candidates = {self.candidates}')
        self.quota = self.evaluate_quota()
        self.log.debug(f'quota = {self.quota}')
        if self.candidates[-1].score[-1][0] > self.quota:
            self.elect(self.candidates[-1])
        else:
            self.discard_weakest()

    def discard_weakest(self):
        candidates_to_discard = []

        if len(self.candidates) <= 1:
            candidates_to_discard.extend(self.candidates)
        elif self.candidates[0].compare(self.candidates[1]) != 0:
            assert self.candidates[0].compare(self.candidates[1]) == -1, f'self.candidates not properly sorted: {self.candidates}'

            candidates_to_discard.append(self.candidates[0])
        else:
            candidates_to_discard.extend(self.get_next_arbitrary_discard())

        self.log.info(f'Discarding {candidates_to_discard}')
        for candidate in candidates_to_discard:
            self.discard(candidate)

    def get_next_arbitrary_discard(self):
        if self.arbitrary_discards_pointer >= len(self.arbitrary_discards):
            self.log.info(f'Arbitrary discard decision needed')
            from lada.dike.maintenance import ArbitraryDiscardDecisionNeededError
            raise ArbitraryDiscardDecisionNeededError(self.candidates)

        self.log.info(f'Using arbitrary discard')
        result = self.arbitrary_discards[self.arbitrary_discards_pointer]
        self.arbitrary_discards_pointer += 1

        return result

    def run(self, threshold=0.4, print_results=False):
        self.log.info(f'Starting new voting. vacancies = {self.vacancies}')
        self.log.debug(f'candidates = {sorted(self.candidates, key=attrgetter("id"))}')
        if feature.is_active(FEATURE_STV_REJECTION):
            self.reject_candidates(threshold)
        while len(self.candidates) > 0 and len(self.elected) < self.vacancies:
            self.round()
        results = {candidate: candidate.score[-1][0] for candidate in self.candidates}
        self.discarded += [candidate for candidate in sorted(results, key=results.get)]
        for candidate in results:
            self.log.info(f'Discarding candidate {candidate} with score {candidate.score[-1][0]}')
            self.results.update({candidate:candidate.score[-1][0]})
        self.log.info(f'Voting finished')
        self.log.info(f'elected = {self.elected}')
        self.log.info(f'discarded = {self.discarded}')
        if feature.is_active(FEATURE_STV_REJECTION):
            self.log.info(f'rejected = {self.rejected}')
        self.log.info(f'Results: {self.results}')
        if print_results:
            print(self.results)
        return self.elected, self.discarded, self.rejected
