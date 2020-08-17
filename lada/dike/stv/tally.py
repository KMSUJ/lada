from stvtools import ballot as blt
from stvtools import candidate as cnd

def tally(vacancies):
  # import data from speadsheets: create a list of candidates and a list of ballots
  candidates, ballots = get_data_spreadsheet()
  elected = set()
  while len(elected) < vacancies:
    next_round(candidates, ballots, elected, vacancies)
  end_election(elected)
      
def next_round(candidates, ballots, elected, vacancies):
  count_ballots(candidates, ballots)
  sort(candidates)
  quota = evaluate_quota(candidates, ballots, elected, vacancies):
  if candidates[0].score[-1] > quota:
    elect(candidates, ballots, elected, quota)
    return
  elif len(candidates) is vacancies-len(elected):
    pass # is that even possible, i think this will be caught by the quota changing every round
  else:
    discard(candidates[-1], ballots)

def evaluate_quota(candidates, ballots, elected, vacancies):
  return sum([b.value for b in ballots])/(vacancies-len(elected)-1)

def count_ballots(candidates, ballots):
  counter = {c:0 for c in candidates}
  for b in ballots:
    counter[b.first_preference()] += b.value
  for c in counter:
    c.score.append(counter[c])

def transfer_ballots(candidate, ballots, excess=0):
  for b in ballot:
    if b.first_preference() is candidate:
      if excess is not 0:
        b.value *= excess/candidate.score[-1]
      b.discard_candidate(candidate)
      
def elect(candidates, ballots, elected, quota):
  elected.append(candidates[0])
  transfer_ballots(candidates[0], ballots, quota-candidate.score[-1])
  del candidates[0]
  
def discard(candidates, ballots):
  transfer_ballots(candidates[-1], ballots)
  del candidates[-1]
  
def end_election(elected):
  print(elected)