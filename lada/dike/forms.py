import lada.fellow

from flask_wtf import FlaskForm
from wtforms import IntegerField, BooleanField, PasswordField, SubmitField, HiddenField
from wtforms.validators import DataRequired

from lada.dike.validators import *

from lada.dike import maintenance


class RegisterForm(FlaskForm):
    kmsid = IntegerField('Numer Legitymacji Kołowej', validators=[DataRequired()])
    boss = BooleanField('Prezes')
    vice = BooleanField('Wiceprezes')
    treasure = BooleanField('Skarbnik')
    secret = BooleanField('Sekretarz')
    library = BooleanField('Bibliotekarz')
    free = BooleanField('Wolny Członek')
    covision = BooleanField('Komisja Rewizyjna')
    password = PasswordField('Hasło Komitetu', validators=[DataRequired()])
    submit = SubmitField('Zarejestruj')


class BallotForm(FlaskForm):
    kmsid = IntegerField('Numer Legitymacji Kołowej', validators=[DataRequired()])
    password = PasswordField('Hasło', validators=[DataRequired()])
    submit = SubmitField('Zagłosuj')


class AfterBallotForm(FlaskForm):
    logout = SubmitField('Wyloguj')


class PanelForm(FlaskForm):
    begin_election = SubmitField('Rozpocznij Wybory')
    begin_voting = SubmitField('Rozpocznij Głosowanie')
    end_voting = SubmitField('Zakończ Głosowanie')
    end_election = SubmitField('Zakończ Wybory')


class ReckoningForm(FlaskForm):
    boss = HiddenField('Prezes', validators=[DataRequired(), ReckoningFieldValidator('boss')])
    vice = HiddenField('Wiceprezes', validators=[DataRequired(), ReckoningFieldValidator('vice')])
    treasure = HiddenField('Skarbnik', validators=[DataRequired(), ReckoningFieldValidator('treasure')])
    secret = HiddenField('Sekretarz', validators=[DataRequired(), ReckoningFieldValidator('secret')])
    library = HiddenField('Bibliotekarz', validators=[DataRequired(), ReckoningFieldValidator('library')])
    free = HiddenField('Wolny Członek', validators=[ReckoningFieldValidator('free', maximum=None)])
    covision = HiddenField('Komisja Rewizyjna', validators=[DataRequired(), ReckoningFieldValidator('covision', maximum=3)])
    password = PasswordField('Hasło Komitetu', validators=[DataRequired()])
    submit = SubmitField('Ustal', validators=[
        ReckoningMaxFellowValidator(8, ['boss', 'vice', 'treasure', 'secret', 'library', 'free']),
        ReckoningNoDuplicatesValidator(['boss', 'vice', 'treasure', 'secret', 'library', 'free', 'covision']),
    ])
