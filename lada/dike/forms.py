from functools import partial

import flask_featureflags as feature

from flask_wtf import FlaskForm
from wtforms import IntegerField, BooleanField, PasswordField, SubmitField, HiddenField, StringField
from wtforms.validators import DataRequired, Regexp

from lada.dike.validators import *

from lada.constants import *


class RegisterForm(FlaskForm):
    kmsid = IntegerField('Numer Legitymacji Kołowej', validators=[DataRequired()])
    boss = BooleanField('Prezes')
    vice = BooleanField('Wiceprezes')
    treasure = BooleanField('Skarbnik')
    secret = BooleanField('Sekretarz')
    library = BooleanField('Bibliotekarz')
    free = BooleanField('Wolny Członek', validators=[RegisterMandatoryPositionValidator(POSITIONS_BOARD)])
    covision = BooleanField('Komisja Rewizyjna')
    password = PasswordField('Hasło Komitetu', validators=[DataRequired()])
    submit = SubmitField('Zarejestruj', validators=[
        ConditionalValidator(
            partial(feature.is_active, FEATURE_DIKE_CANDIDATE_BOARD_COVISION_CONFLICT_FORBIDDEN),
            RegisterConflictValidator(POSITIONS_BOARD, [POSITION_COVISION])
        ),
        RegistrationTotalPositionsLimitValidator(POSITIONS_BOARD, 4),
    ])


class BallotForm(FlaskForm):
    submit = SubmitField('Zagłosuj', validators=[DynamicBallotDuplicateDetector()])


class AfterBallotForm(FlaskForm):
    logout = SubmitField('Wyloguj')


class PanelForm(FlaskForm):
    begin_election = SubmitField('Rozpocznij Wybory')
    begin_voting_boss = SubmitField('Rozpocznij Głosowanie na Prezesa')
    begin_voting_board = SubmitField('Rozpocznij Głosowanie na Zarząd')
    begin_voting_covision = SubmitField('Rozpocznij Głosowanie na Komisję')
    end_voting = SubmitField('Zakończ Głosowanie')
    end_election = SubmitField('Zakończ Wybory')
    unregister_candidates = SubmitField('Usuń Kandydatów')

class ReckoningFormBoss(FlaskForm):
    choose_boss = SubmitField('Kontynuuj')

class ReckoningFormBoard(FlaskForm):
    vice = HiddenField('Wiceprezes', validators=[DataRequired(), ReckoningFieldValidator(POSITION_VICE)])
    treasure = HiddenField('Skarbnik', validators=[DataRequired(), ReckoningFieldValidator(POSITION_TREASURE)])
    secret = HiddenField('Sekretarz', validators=[DataRequired(), ReckoningFieldValidator(POSITION_SECRET)])
    library = HiddenField('Bibliotekarz', validators=[DataRequired(), ReckoningFieldValidator(POSITION_LIBRARY)])
    free = HiddenField('Wolny Członek', validators=[ReckoningFieldValidator(POSITION_FREE, maximum=None)])
    password = PasswordField('Hasło Komitetu', validators=[DataRequired()])
    choose_board = SubmitField('Ustal', validators=[
        ReckoningMaxFellowValidator(7, [POSITION_VICE, POSITION_TREASURE, POSITION_SECRET, POSITION_LIBRARY, POSITION_FREE]),
        ReckoningNoDuplicatesValidator([POSITION_VICE, POSITION_TREASURE, POSITION_SECRET, POSITION_LIBRARY, POSITION_FREE]),
    ])

class ReckoningFormCovision(FlaskForm):
    choose_covision = SubmitField('Kontynuuj')

class EndscreenForm(FlaskForm):
    submit = SubmitField('Ustal')

class ArbitraryDiscardDecisionForm(FlaskForm):
    position = HiddenField()
    candidates = StringField('Kandydaci')
    submit = SubmitField('Usuń')
