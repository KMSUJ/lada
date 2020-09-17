from flask_wtf import FlaskForm
from wtforms import IntegerField, BooleanField, PasswordField, SubmitField, HiddenField
from wtforms.validators import ValidationError, DataRequired, Optional

class RegisterForm(FlaskForm):
  studentid = IntegerField('Numer Legitymacji', validators=[DataRequired()])
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
  studentid = IntegerField('Numer Legitymacji', validators=[DataRequired()])
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
  boss = HiddenField('Prezes', validators=[DataRequired()])
  vice = HiddenField('Wiceprezes', validators=[DataRequired()])
  treasure = HiddenField('Skarbnik', validators=[DataRequired()])
  secret = HiddenField('Sekretarz', validators=[DataRequired()])
  library = HiddenField('Bibliotekarz', validators=[DataRequired()])
  free = HiddenField('Wolny Członek')
  covision = HiddenField('Komisja Rewizyjna', validators=[DataRequired()])
  password = PasswordField('Hasło Komitetu', validators=[DataRequired()])
  submit = SubmitField('Ustal')
