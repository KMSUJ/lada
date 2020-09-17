class Tally():
  def __init__(self, ballots, vacancies = 1):
    self.ballots = ballots
    self.vacancies = vacancies
    self.candidates = self.read_candidates()
    self.elected = list()
    self.discarded = list()
    self.rejected = set()
    self.quota = self.evaluate_quota()

  def read_candidates(self):
    return list({candidate for ballot in self.ballots for candidate in set(ballot.preference) | ballot.reject})

  def evaluate_quota(self):
    return sum([ballot.value for ballot in self.ballots])/(self.vacancies-len(self.elected)+1)

  def reject_candidates(self, threshold = 0.4):
    for candidate in self.candidates:
      if len([ballot for ballot in self.ballots if candidate in ballot.reject]) > threshold * len(self.ballots):
        self.rejected.add(candidate)
        self.transfer_ballots(candidate)
        self.candidates.remove(candidate)

  def transfer_ballots(self, candidate, excess = 0):
    for ballot in self.ballots:
      if candidate in ballot.preference: 
        if ballot.first_preference() == candidate:
          if excess > 0:
            ballot.value *= excess/candidate.score[-1]
        ballot.discard(candidate)

  def elect(self, candidate):
    self.elected.append(candidate)
    self.transfer_ballots(candidate, self.quota-candidate.score[-1])
    self.candidates.remove(candidate)

  def discard(self, candidate):
    self.discarded.append(candidate)
    self.transfer_ballots(candidate)
    self.candidates.remove(candidate)

  def count_votes(self):
    counter = {candidate:0 for candidate in self.candidates}
    for ballot in self.ballots:
      if ballot.value > 0:
        counter[ballot.first_preference()] += ballot.value
    return counter

  def score_votes(self, votes):
    for candidate in votes:
      candidate.score.append(votes[candidate])

  def round(self):
    self.score_votes(self.count_votes())
    self.candidates.sort()
    self.quota = self.evaluate_quota()
    if self.candidates[0].score[-1] > self.quota:
      self.elect(self.candidates[0])
    else:
      self.discard(self.candidates[-1])

  def run(self, threshold = 0.4):
    self.reject_candidates(threshold)
    while len(self.candidates) > 0 and len(self.elected) < self.vacancies:
      self.round()
    results = {candidate:candidate.score[-1] for candidate in self.candidates}
    self.discarded += [candidate for candidate in sorted(results, key=results.get)]
    return self.elected, self.discarded, self.rejected

  def print_results(self):
    for candidate in self.candidates:
      print(f'{candidate.name} : candidate.score[-1]')
