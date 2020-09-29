from functools import partial

import flask_featureflags as feature

from flask_wtf import FlaskForm
from wtforms import IntegerField, BooleanField, PasswordField, SubmitField, HiddenField
from wtforms.validators import DataRequired

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
            partial(feature.is_active, 'dike_candidate_board_covision_conflict_forbidden'),
            RegisterConflictValidator(POSITIONS_BOARD, [POSITION_COVISION])
        )
    ])


class BallotForm(FlaskForm):
    kmsid = IntegerField('Numer Legitymacji Kołowej', validators=[DataRequired()])
    password = PasswordField('Hasło', validators=[DataRequired()])
    submit = SubmitField('Zagłosuj', validators=[DynamicBallotDuplicateDetector()])


class AfterBallotForm(FlaskForm):
    logout = SubmitField('Wyloguj')


class PanelForm(FlaskForm):
    begin_election = SubmitField('Rozpocznij Wybory')
    begin_voting = SubmitField('Rozpocznij Głosowanie')
    end_voting = SubmitField('Zakończ Głosowanie')
    end_election = SubmitField('Zakończ Wybory')


class ReckoningForm(FlaskForm):
    boss = HiddenField('Prezes', validators=[DataRequired(), ReckoningFieldValidator(POSITION_BOSS)])
    vice = HiddenField('Wiceprezes', validators=[DataRequired(), ReckoningFieldValidator(POSITION_VICE)])
    treasure = HiddenField('Skarbnik', validators=[DataRequired(), ReckoningFieldValidator(POSITION_TREASURE)])
    secret = HiddenField('Sekretarz', validators=[DataRequired(), ReckoningFieldValidator(POSITION_SECRET)])
    library = HiddenField('Bibliotekarz', validators=[DataRequired(), ReckoningFieldValidator(POSITION_LIBRARY)])
    free = HiddenField('Wolny Członek', validators=[ReckoningFieldValidator(POSITION_FREE, maximum=None)])
    covision = HiddenField('Komisja Rewizyjna', validators=[DataRequired(), ReckoningFieldValidator(POSITION_COVISION, maximum=3)])
    password = PasswordField('Hasło Komitetu', validators=[DataRequired()])
    submit = SubmitField('Ustal', validators=[
        ReckoningMaxFellowValidator(8, [POSITION_BOSS, POSITION_VICE, POSITION_TREASURE, POSITION_SECRET, POSITION_LIBRARY, POSITION_FREE]),
        ReckoningNoDuplicatesValidator([POSITION_BOSS, POSITION_VICE, POSITION_TREASURE, POSITION_SECRET, POSITION_LIBRARY, POSITION_FREE, POSITION_COVISION]),
    ])
