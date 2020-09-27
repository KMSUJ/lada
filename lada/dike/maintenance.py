import datetime
import logging
from sqlalchemy import desc
from lada import db
from lada.models import Fellow, Position, Election
from lada.fellow.board import position as board, clear_board
from lada.dike.stv.ballot import Ballot
from lada.dike.stv.candidate import Candidate
from lada.dike.stv.tally import Tally

log = logging.getLogger(__name__)


def set_board(form):
  clear_board()
  boss = Fellow.query.filter_by(id=form.boss.data).first()
  boss.set_board('board', True)
  boss.set_board('boss', True)
  vice = Fellow.query.filter_by(id=form.vice.data).first()
  vice.set_board('board', True)
  vice.set_board('vice', True)
  treasure = Fellow.query.filter_by(id=form.treasure.data).first()
  treasure.set_board('board', True)
  treasure.set_board('treasure', True)
  secret = Fellow.query.filter_by(id=form.secret.data).first()
  secret.set_board('board', True)
  secret.set_board('secret', True)
  library = Fellow.query.filter_by(id=form.library.data).first()
  library.set_board('board', True)
  library.set_board('library', True)
  frees = form.free.data.split("+")
  if '' in frees:
    frees.remove('')
  if frees is not None:
    for j in frees:
      free = Fellow.query.filter_by(id=j).first()
      free.set_board('board', True)
      free.set_board('free', True)
  for j in form.covision.data.split("+"):
    covision = Fellow.query.filter_by(id=j).first()
    covision.set_board('covision', True)

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
    position = Position(name=board[p], flagname=p)
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
  vacancies = 1 if position.name == 'Prezes' else 3
  return Tally(ballots, vacancies).run()

def reckon_election(election):
  results = list()
  for position in election.positions.all():
    elected, discarded, rejected = reckon_position(position)
    results.append({'position':position, 
      'elected':[Fellow.query.filter_by(id=candidate.id).first() for candidate in elected],
      'discarded':[Fellow.query.filter_by(id=candidate.id).first() for candidate in reversed(discarded)],
      'rejected':[Fellow.query.filter_by(id=candidate.id).first() for candidate in rejected], })
  return results

def begin_election():
  log.info('Starting election')
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

def end_election(election):
  election.set_flag('active', False)
  db.session.commit()
