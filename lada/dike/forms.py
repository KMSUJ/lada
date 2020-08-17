from flask_wtf import FlaskForm
from wtforms import IntegerField, BooleanField, PasswordField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Optional

class RegisterForm(FlaskForm):
  studentid = IntegerField('Numer Legitymacji', validators=[DataRequired()])
  prezes = BooleanField('Prezes')
  vice = BooleanField('Viceprezes')
  skarbnik = BooleanField('Skarbnik')
  sekretarz = BooleanField('Sekretarz')
  bibliotekarz = BooleanField('Bibliotekarz')
  wolny = BooleanField('Wolny Członek')
  komisja = BooleanField('Komisja Rewizyjna')
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
