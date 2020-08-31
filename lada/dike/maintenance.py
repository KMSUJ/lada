import datetime
from sqlalchemy import desc
from lada import db
from lada.models import Position, Election
from lada.fellow.board import position as board

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

def count_votes():
  pass

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
  count_votes()

def end_election(election):
  election.set_flag('active', False)
  db.session.commit()
