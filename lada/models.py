import logging
from time import time

import jwt
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from lada import db, login
from lada.modules import flags

log = logging.getLogger(__name__)

board_flags = {
    'active': flags.f(1),
    'fellow': flags.f(2),
    'board': flags.f(3),
    'boss': flags.f(4),
    'vice': flags.f(5),
    'treasure': flags.f(6),
    'secret': flags.f(7),
    'library': flags.f(8),
    'free': flags.f(9),
    'covision': flags.f(10)
}

news_flags = {
    'wycinek': flags.f(1),
    'cnfrnce': flags.f(2),
    'anteomnia': flags.f(3),
    'fotki': flags.f(4),
    'fszysko': flags.f(5)
}

election_flags = {
    'active': flags.f(1),
    'register': flags.f(2),
    'voting': flags.f(3)
}

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
        db.session.commit()

    def add_voter(self, fellow):
        self.voters.append(fellow)
        db.session.commit()

    def did_vote(self, fellow):
        return self.voters.filter_by(id=fellow.id).count() > 0

    def count_votes(self):
        return self.voters.count()

    # flag methods
    def set_flag(self, flag, value):
        self.flags = flags.assign(self.flags, election_flags[flag], value)
        db.session.commit()

    def check_flag(self, flag):
        return flags.check(self.flags, election_flags[flag])

    def __repr__(self):
        return f'<Election {self.id}/{self.year}>'


class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    position_id = db.Column(db.Integer, db.ForeignKey('position.id'))
    preference = db.Column(db.PickleType)
    reject = db.Column(db.PickleType)

    def __repr__(self):
        return f'<Vote #{self.id}>'


candidates = db.Table('candidates',
                      db.Column('position_id', db.Integer, db.ForeignKey('position.id'), primary_key=True),
                      db.Column('fellow_id', db.Integer, db.ForeignKey('fellow.id'), primary_key=True)
                      )

candidates_elected = db.Table('candidates_elected',
                              db.Column('position_id', db.Integer, db.ForeignKey('position.id'), primary_key=True),
                              db.Column('fellow_id', db.Integer, db.ForeignKey('fellow.id'), primary_key=True)
                              )

candidates_discarded = db.Table('candidates_discarded',
                                db.Column('position_id', db.Integer, db.ForeignKey('position.id'), primary_key=True),
                                db.Column('fellow_id', db.Integer, db.ForeignKey('fellow.id'), primary_key=True)
                                )

candidates_rejected = db.Table('candidates_rejected',
                               db.Column('position_id', db.Integer, db.ForeignKey('position.id'), primary_key=True),
                               db.Column('fellow_id', db.Integer, db.ForeignKey('fellow.id'), primary_key=True)
                               )



class Position(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    election_id = db.Column(db.Integer, db.ForeignKey('election.id'))
    name = db.Column(db.String(24))
    flagname = db.Column(db.String(24))
    candidates = db.relationship('Fellow', secondary=candidates, lazy='dynamic',
                                 backref=db.backref('position', lazy=True))
    votes = db.relationship('Vote', backref='position', lazy='dynamic')

    is_reckoned = db.Column(db.Boolean(False))
    elected = db.relationship('Fellow', secondary=candidates_elected, lazy='dynamic',
                              backref=db.backref('position_elected', lazy=True))
    discarded = db.relationship('Fellow', secondary=candidates_discarded, lazy='dynamic',
                                backref=db.backref('position_discarded', lazy=True))
    rejected = db.relationship('Fellow', secondary=candidates_rejected, lazy='dynamic',
                               backref=db.backref('position_rejected', lazy=True))

    def __repr__(self):
        return f'<Position {self.name}>'

    def register(self, fellow):
        log.info(f"Registering candidate {fellow} for {self}")
        if not self.is_registered(fellow):
            self.candidates.append(fellow)
        db.session.commit()

    def unregister(self, fellow):
        if self.is_registered(fellow):
            self.candidates.remove(fellow)
        db.session.commit()

    def is_registered(self, fellow):
        return self.candidates.filter_by(id=fellow.id).count() > 0

    def store_vote(self, vote):
        self.votes.append(vote)
        db.session.commit()


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

    def __repr__(self):
        return f'<Fellow {self.email}>'

    def repr(self):
        return f'{self.name} {self.surname}'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # flag methods
    def set_board(self, flag, value):
        self.board = flags.assign(self.board, board_flags[flag], value)

    def check_board(self, flag):
        return flags.check(self.board, board_flags[flag])

    def is_board(self, *position):
        return self.check_board('boss') or self.check_board('vice') or any(self.check_board(pos) for pos in position)

    def set_newsletter(self, flag, value):
        self.newsletter = flags.assign(self.newsletter, news_flags[flag], value)

    def check_newsletter(self, flag):
        return flags.check(self.newsletter, news_flags[flag])

    # password reset methods
    def get_password_reset_token(self, expires_in=60 * 12):
        return jwt.encode(
            {'password_reset': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['password_reset']
        except:
            return
        return Fellow.query.get(id)


tags = db.Table('tags',
                db.Column('article_id', db.Integer, db.ForeignKey('article.id'), primary_key=True),
                db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
                )


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(144))
    posted = db.Column(db.DateTime)
    body = db.Column(db.String)
    tags = db.relationship('Tag', secondary=tags, lazy='dynamic', backref=db.backref('article', lazy=True))

    def __repr__(self):
        return f'<Article {self.id}>'

    def add_tag(self, tag):
        if not self.has_tag(tag):
            self.tags.append(tag)

    def remove_tag(self, tag):
        if self.has_tag(tag):
            self.tags.remove(tag)

    def clear_tags(self):
        for tag in self.tags:
            self.remove_tag(tag)

    def has_tag(self, tag):
        return self.tags.filter_by(id=tag.id).count() > 0


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    line = db.Column(db.String(36))
    articles = db.relationship('Article', viewonly=True, secondary=tags, lazy='dynamic',
                               backref=db.backref('tag', lazy=True))

    def __repr__(self):
        return f'<Tag {self.line}>'
