import logging
import operator
from datetime import datetime
from functools import reduce
from time import time

import jwt
from flask import current_app
from flask_login import UserMixin
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash

from lada import db, login
from lada.constants import *
from lada.modules import flags

log = logging.getLogger(__name__)

board_flags = {
    FELLOW_ACTIVE: flags.f(1),
    FELLOW_FELLOW: flags.f(2),
    FELLOW_BOARD: flags.f(3),
    POSITION_BOSS: flags.f(4),
    POSITION_VICE: flags.f(5),
    POSITION_TREASURE: flags.f(6),
    POSITION_SECRET: flags.f(7),
    POSITION_LIBRARY: flags.f(8),
    POSITION_FREE: flags.f(9),
    POSITION_COVISION: flags.f(10)
}

news_flags = {
    NEWS_WYCINEK: flags.f(1),
    NEWS_CONFERENCE: flags.f(2),
    NEWS_ANTEOMNIA: flags.f(3),
    NEWS_PHOTO: flags.f(4),
    NEWS_FSZYSKO: flags.f(5)
}

news_flags[NEWS_ALL] = reduce(operator.or_, news_flags.values())

election_flags = {
    ELECTION_ACTIVE: flags.f(1),
    ELECTION_REGISTER: flags.f(2),
    ELECTION_VOTING: flags.f(3)
}

voters_boss = db.Table('voters_boss',
                  db.Column('election_id', db.Integer, db.ForeignKey('election.id'), primary_key=True),
                  db.Column('fellow_id', db.Integer, db.ForeignKey('fellow.id'), primary_key=True)
                  )

voters_board = db.Table('voters_board',
                  db.Column('election_id', db.Integer, db.ForeignKey('election.id'), primary_key=True),
                  db.Column('fellow_id', db.Integer, db.ForeignKey('fellow.id'), primary_key=True)
                  )

voters_covision = db.Table('voters_covision',
                  db.Column('election_id', db.Integer, db.ForeignKey('election.id'), primary_key=True),
                  db.Column('fellow_id', db.Integer, db.ForeignKey('fellow.id'), primary_key=True)
                  )


entitled_to_vote = db.Table('entitled_to_vote',
                            db.Column('election_id', db.Integer, db.ForeignKey('election.id'), primary_key=True),
                            db.Column('fellow_id', db.Integer, db.ForeignKey('fellow.id'), primary_key=True)
                            )


class Election(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    flags = db.Column(db.Integer)
    stage = db.Column(db.String())
    positions = db.relationship('Position', backref='election', lazy='dynamic')
    voters_boss = db.relationship('Fellow', secondary=voters_boss, lazy='dynamic', backref=db.backref('election_boss', lazy=True))
    voters_board = db.relationship('Fellow', secondary=voters_board, lazy='dynamic', backref=db.backref('election_board', lazy=True))
    voters_covision = db.relationship('Fellow', secondary=voters_covision, lazy='dynamic', backref=db.backref('election_covision', lazy=True))

    is_entitled_to_vote_reckoned = db.Column(db.Boolean)
    entitled_to_vote = db.relationship('Fellow', secondary=entitled_to_vote, lazy='dynamic', backref=db.backref('election_entitled_to_vote', lazy=True))

    def __repr__(self):
        return f'<Election of {self.year} #{self.id}>'

    def __str__(self):
        return f'Election of the year {self.year}'

    def add_position(self, position):
        self.positions.append(position)
        db.session.commit()

    def add_voter(self, fellow):
        if self.is_stage(STAGE_BOSS):
            self.voters_boss.append(fellow)
            db.session.commit()
        elif self.is_stage(STAGE_BOARD):
            self.voters_board.append(fellow)
            db.session.commit()
        elif self.is_stage(STAGE_COVISION):
            self.voters_covision.append(fellow)
            db.session.commit()

    def is_entitled_to_vote(self, fellow):
        from lada.dike.maintenance import reckon_entitled_to_vote
        entitled = reckon_entitled_to_vote(self)
        return fellow.id in map(lambda x: x.id, entitled)

    def did_vote(self, fellow):
        if self.is_stage(STAGE_BOSS):
            return self.voters_boss.filter_by(id=fellow.id).count() > 0
        elif self.is_stage(STAGE_BOARD):
            return self.voters_board.filter_by(id=fellow.id).count() > 0
        elif self.is_stage(STAGE_COVISION):
            return self.voters_covision.filter_by(id=fellow.id).count() > 0

    def count_votes(self):
        if self.is_stage(STAGE_BOSS):
            return self.voters_boss.count()
        elif self.is_stage(STAGE_BOARD):
            return self.voters_board.count()
        elif self.is_stage(STAGE_COVISION):
            return self.voters_covision.count()

    def set_stage(self, stage):
        self.stage = stage
        db.session.commit()

    def is_stage(self, stage):
        return self.stage == stage
            

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

candidates_chosen = db.Table('candidates_chosen',
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

arbitrary_discard_fellow = db.Table('arbitrary_discard_fellow',
                                    db.Column('arbitrary_discard_id', db.Integer, db.ForeignKey('arbitrary_discard.id'), primary_key=True),
                                    db.Column('fellow_id', db.Integer, db.ForeignKey('fellow.id'), primary_key=True)
                                    )


class ArbitraryDiscard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    position_id = db.Column(db.Integer, db.ForeignKey('position.id'))

    discarded = db.relationship('Fellow', secondary=arbitrary_discard_fellow, lazy='dynamic')


class Position(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    election_id = db.Column(db.Integer, db.ForeignKey('election.id'))
    name = db.Column(db.String(24))
    repname = db.Column(db.String(24))
    candidates = db.relationship('Fellow', secondary=candidates, lazy='dynamic',
                                 backref=db.backref('position', lazy=True))
    votes = db.relationship('Vote', backref='position', lazy='dynamic')

    is_reckoned = db.Column(db.Boolean(False))
    chosen = db.relationship('Fellow', secondary=candidates_chosen, lazy='dynamic',
                              backref=db.backref('position_chosen', lazy=True))
    elected = db.relationship('Fellow', secondary=candidates_elected, lazy='dynamic',
                              backref=db.backref('position_elected', lazy=True))
    discarded = db.relationship('Fellow', secondary=candidates_discarded, lazy='dynamic',
                                backref=db.backref('position_discarded', lazy=True))
    rejected = db.relationship('Fellow', secondary=candidates_rejected, lazy='dynamic',
                               backref=db.backref('position_rejected', lazy=True))

    arbitrary_discards = db.relationship(ArbitraryDiscard, backref="position")

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

    def choose(self, fellow):
        log.info(f"Choosing candidate {fellow} for {self}")
        if not self.is_chosen(fellow):
            self.chosen.append(fellow)
        db.session.commit()
    
    def is_registered(self, fellow):
        return self.candidates.filter_by(id=fellow.id).count() > 0

    def is_chosen(self, fellow):
        log.debug(f'{self.chosen.all()}')
        return self.chosen.filter_by(id=fellow.id).count() > 0
    
    def store_vote(self, vote):
        self.votes.append(vote)
        db.session.commit()

    def append_arbitrary_discard(self, fellows):
        discard = ArbitraryDiscard()
        discard.discarded = fellows
        self.arbitrary_discards.append(discard)
        db.session.commit()


rodo = db.Table('rodo',
                      db.Column('rodo_id', db.Integer, db.ForeignKey('rodos.id'), primary_key=True),
                      db.Column('fellow_id', db.Integer, db.ForeignKey('fellow.id'), primary_key=True)
                      )

class Rodos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String)


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
    kmsid = db.Column(db.Integer, unique=True)
    studentid = db.Column(db.Integer, unique=True)

    verified = db.Column(db.Boolean, default=False)

    #rodo
    rodo = db.relationship('Rodos', secondary=rodo, lazy='dynamic',
                                 backref=db.backref('fellow', lazy=True))

    def add_rodo(self, rodo):
        if not self.has_rodo(rodo):
            self.rodo.append(rodo)

    def remove_rodo(self, rodo):
        if self.has_rodo(rodo):
            self.rodo.remove(rodo)

    def has_tag(self, rodo):
        return self.rodo.filter_by(id=rodo.id).count() > 0

    # flags
    board = db.Column(db.Integer)
    newsletter = db.Column(db.Integer)

    shirt = db.Column(db.String(4))
    phone = db.Column(db.Integer)

    def __repr__(self):
        return f'<Fellow {self.email}>'

    def __str__(self):
        return f'{self.name} {self.surname}'

    def repr(self):
        return f'{self.name} {self.surname}'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        db.session.commit()

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # flag methods
    def set_board(self, flag, value):
        self.board = flags.assign(self.board, board_flags[flag], value)
        log.debug(f'Setting the {flag} flag to {value} for fellow {self}')
        db.session.commit()

    def check_board(self, flag):
        return self.verified and flags.check(self.board, board_flags[flag])

    def is_board(self, *position):
        return self.check_board(FELLOW_BOARD) or self.check_board(POSITION_BOSS) or self.check_board(POSITION_VICE) or any(self.check_board(pos) for pos in position)

    def set_newsletter(self, flag, value):
        self.newsletter = flags.assign(self.newsletter, news_flags[flag], value)
        db.session.commit()

    def check_newsletter(self, flag):
        return flags.check(self.newsletter, news_flags[flag])

    # password reset methods
    def get_password_reset_token(self, expires_in=60 * 12):
        return jwt.encode(
            {'password_reset': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    def get_verification_token(self, expires_in=60 * 12):
        return jwt.encode(
            {'verify': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    def activate(self):
        if self.kmsid is None:
            self.joined = datetime.utcnow()
            self.kmsid = self.next_kmsid()
        self.set_board(FELLOW_ACTIVE, True)

    def deactivate(self):
        self.set_board(FELLOW_ACTIVE, False)

    @staticmethod
    def decode_reset_password_token(token):
        try:
            decoded = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            fellow_id = decoded['password_reset']
            return Fellow.query.get(fellow_id)
        except:
            return

    def set_verified(self, value):
        self.verified = value
        db.session.commit()

    @staticmethod
    def decode_verification_token(token):
        try:
            decoded = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            fellow_id = decoded['verify']
            return Fellow.query.get(fellow_id)
        except:
            return None

    @staticmethod
    def next_kmsid():
        max_kmsid = db.session.query(func.max(Fellow.kmsid)).scalar()
        if max_kmsid is None:
            max_kmsid = 0
        return max_kmsid + 1


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
