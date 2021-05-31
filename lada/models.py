import logging
from time import time

import jwt
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from lada import db, login

log = logging.getLogger(__name__)


# fellows - website admins and moderators

@login.user_loader
def load_user(id):
    return Fellow.query.get(int(id))


class Fellow(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(144), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    verified = db.Column(db.Boolean, default=False)

    # flags
    admin = db.Column(db.Boolean, default=False)
    redactor = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Fellow {self.email}>'

    def __str__(self):
        return self.__repr__()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        db.session.commit()

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # flag methods
    def set_admin(self, value):
        self.admin = value
        log.debug(f'Setting the admin flag to {value} for fellow {self}')
        db.session.commit()

    def check_admin(self):
        return self.verified and self.admin

    def set_redactor(self, value):
        self.redactor = value
        log.debug(f'Setting the redactor flag to {value} for fellow {self}')
        db.session.commit()

    def check_redactor(self):
        return self.verified and self.redactor


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


# articles

tags = db.Table('tags',
                db.Column('article_id', db.Integer, db.ForeignKey('article.id'), primary_key=True),
                db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
                )


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(144))
    posted = db.Column(db.DateTime)
    body = db.Column(db.String)
    tags = db.relationship(
            'Tag',
            secondary=tags,
            lazy='dynamic',
            backref=db.backref('article', lazy=True),
            )

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
