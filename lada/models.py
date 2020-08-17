from lada import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from lada.modules import flags as fg

brdfg = {'active':fg.f(1), 'fellow':fg.f(2), 'board':fg.f(3), 'president':fg.f(4), 'vice':fg.f(5), 'treasurer':fg.f(6), 'secretary':fg.f(7), 'librarian':fg.f(8), 'revision':fg.f(9)}
nwsfg = {'wycinek':fg.f(1), 'cnfrnce':fg.f(2)}
elcfg = {'active':fg.f(1), 'register':fg.f(2), 'voting':fg.f(3)}

voters = db.Table('voters',
    db.Column('election_id', db.Integer, db.ForeignKey('election.id'), primary_key=True),
    db.Column('fellow_id', db.Integer, db.ForeignKey('fellow.id'), primary_key=True)
)

class Election(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  year = db.Column(db.Integer)
  flags = db.Column(db.Integer)
  positions = db.relationship('Position', backref='election', lazy='dynamic')
  voters = db.relationship('Fellow', secondary=voters, lazy='dynamic', backref=db.backref('election', lazy=True))

  def __repr__(self):
    return f'<Election of {self.year} #{self.id}>'

  def add_position(self, position):
    self.positions.append(position)

  def add_voter(self, fellow):
    self.voters.append(fellow)

  def did_vote(self, fellow):
    return self.voters.filter_by(id = fellow.id).count() > 0
  
  # flag methods
  def set_flag(self, flag, value):
    self.flags = fg.assign(self.flags, elcfg[flag], value)

  def check_flag(self, flag):
    return fg.check(self.flags, elcfg[flag])

class Vote(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  position_id = db.Column(db.Integer, db.ForeignKey('position.id'))
  preference = db.Column(db.PickleType)
  reject = db.Column(db.PickleType)

  def __repr__(self):
    return f'<Vote #{id}>'

candidates = db.Table('candidates',
    db.Column('position_id', db.Integer, db.ForeignKey('position.id'), primary_key=True),
    db.Column('fellow_id', db.Integer, db.ForeignKey('fellow.id'), primary_key=True)
)

class Position(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  election_id = db.Column(db.Integer, db.ForeignKey('election.id'))
  name = db.Column(db.String(24))
  candidates = db.relationship('Fellow', secondary=candidates, lazy='dynamic', backref=db.backref('position', lazy=True))
  votes = db.relationship('Vote', backref='position', lazy='dynamic')

  def __repr__(self):
    return f'<Position {self.name}>'

  def register(self, fellow):
    if not self.is_registered(fellow):
      self.candidates.append(fellow)

  def unregister(self, fellow):
    if self.is_registered(fellow):
      self.candidates.remove(user)

  def is_registered(self, fellow):
    return self.candidates.filter_by(id = fellow.id).count() > 0

  def store_vote(self, vote):
    self.votes.append(vote)

@login.user_loader
def load_user(id):
  return Fellow.query.get(int(id))

class Fellow(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(144), index=True, unique=True)
  password_hash = db.Column(db.String(128))

  name = db.Column(db.String(24))
  surname = db.Column(db.String(72))
  joined = db.Column(db.DateTime)
  studentid = db.Column(db.Integer, unique=True)

  # flags
  board = db.Column(db.Integer)
  newsletter = db.Column(db.Integer)
  
  shirt = db.Column(db.String(4))
  phone = db.Column(db.Integer)
  adresses = db.relationship('Adress', backref='fellow', lazy='dynamic')
  
  def __repr__(self):
    return f'<Fellow {self.name} {self.surname}>'

  def repr(self):
    return f'{self.name} {self.surname}'

  def set_password(self, password):
    self.password_hash = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password_hash, password)

  # flag methods
  def set_board(self, flag, value):
    self.board = fg.assign(self.board, brdfg[flag], value)

  def check_board(self, flag):
    return fg.check(self.board, brdfg[flag])
  
  def set_newsletter(self, flag, value):
    self.newsletter = fg.assign(self.newsletter, nwsfg[flag], value)

  def check_newsletter(self, flag):
    return fg.check(self.newsletter, nwsfg[flag])

class Adress(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  fellow_id = db.Column(db.Integer, db.ForeignKey('fellow.id'))
  street = db.Column(db.String(144))
  parcel = db.Column(db.String(12))
  flat = db.Column(db.String(12))
  city = db.Column(db.String(72))
  postcode = db.Column(db.String(12))

  def __repr__(self):
    return f'Adress {street} {parcel}/{flat}\n{city} {postcode}'
