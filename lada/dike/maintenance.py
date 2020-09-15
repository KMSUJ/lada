import datetime
from sqlalchemy import desc
from lada import db
from lada.models import Position, Election
from lada.fellow.board import position as board
from lada.dike.stv.ballot import Ballot
from lada.dike.stv.candidate import Candidate
from lada.dike.stv.tally import Tally

def get_election():
  for e in Election.query.order_by(desc(Election.id)).all():
    if e.check_flag('active'):
      return e
  # warn there is no election  
  return None

def get_electoral(election = None):
  if election is None:
    election = get_election()
  return {election.positions.filter_by(name=board[p]).first():election.positions.filter_by(name=board[p]).first().candidates.all() for p in board}

def create_positions(election):
  for p in board:
    position = Position(name=board[p])
    db.session.add(position)
    election.add_position(position)
  db.session.commit()

def clear_positions():
  positions = Position.query.all()
  for position in positions:
    db.session.delete(position)
  db.session.commit()

def reckon_position(position):
  ballots = set()
  for vote in position.votes.all():
    preference = [Candidate(id=studentid) for studentid in vote.preference]
    reject = {Candidate(id=studentid) for studentid in vote.reject}
    ballots.add(Ballot(preference, reject))
  tally = Tally(ballots, 3) # or one if position is boss - code that in somehow
  elected, discarded = tally.run()
  return elected, discarded

def reckon_election(election):
  for position in election.positions.all():
    elected,discarded = reckon_position(position)
    print(position.name)
    print({c.id:elected[c] for c in elected})
    print('---')
    print({c.id:discarded[c] for c in discarded})
  # return those results

def begin_election():
  election = Election(year=datetime.datetime.utcnow().year)
  election.set_flag('active', True)
  db.session.add(election)
  create_positions(election)
  election.set_flag('register', True)
  db.session.commit()

def begin_voting(election):
  election.set_flag('register', False)
  election.set_flag('voting', True)
  db.session.commit()

def end_voting(election):
  election.set_flag('voting', False)
  db.session.commit()
  reckon_election(election)

def end_election(election):
  election.set_flag('active', False)
  db.session.commit()
