from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from lada.models import Fellow

class LoginForm(FlaskForm):
  email = StringField('Email', validators=[DataRequired()])
  password = PasswordField('Password', validators=[DataRequired()])
  remember_me = BooleanField('Remember Me')
  submit = SubmitField('Log In')

class RegisterForm(FlaskForm):
  email = StringField('Email', validators=[DataRequired(), Email()])
  name = StringField('Name', validators=[DataRequired()])
  surname = StringField('Surame', validators=[DataRequired()])
  studentid = IntegerField('Student Id')
  password = PasswordField('Password', validators=[DataRequired()])
  repassword = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
  submit = SubmitField('Register')

  def validate_email(self, email):
    fellow = Fellow.query.filter_by(email=email.data).first()
    if fellow is not None:
      raise ValidationError('This email adress is already in the database.')

class EditForm(FlaskForm):
  name = StringField('Name', validators=[DataRequired()])
  surname = StringField('Surame', validators=[DataRequired()])
  studentid = IntegerField('Student Id')
  phone = IntegerField('Phone')
  shirt = StringField('Shirt Size')
  submit = SubmitField('Save')

class AdressForm(FlaskForm):
  street = StringField('Street')
  parcel = StringField('Parcel')
  flat = StringField('Flat')
  city = StringField('City')
  postcode = StringField('Postcode')
