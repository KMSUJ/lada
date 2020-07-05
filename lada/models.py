from lada import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Fellow(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(144), index=True, unique=True)
  password_hash = db.Column(db.String(128))

  name = db.Column(db.String(24))
  surname = db.Column(db.String(72))
  joined = db.Column(db.DateTime)
  studentid = db.Column(db.Integer, unique=True)

  #flags
  board = db.Column(db.Integer)
  newsletter = db.Column(db.Integer)
  
  shirt = db.Column(db.String(4))
  phone = db.Column(db.Integer)
  adresses = db.relationship('Adress', backref='fellow', lazy='dynamic')
  
  def __repr__(self):
    return f'<Fellow {name} {surname}>'

  def set_password(self, password):
    self.password_hash = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
  return Fellow.query.get(int(id))

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
