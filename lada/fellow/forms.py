from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Reset')


class PasswordResetForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    repassword = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset')

"""
# those features can be reimplemented to supplement cli
class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    repassword = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        fellow = Fellow.query.filter_by(email=email.data).first()
        if fellow is not None:
            raise ValidationError('This email adress is already in the database.')

class EditForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    studentid = IntegerField('Student Id', validators=[Optional()])
    phone = IntegerField('Phone', validators=[Optional()])
    shirt = StringField('Shirt Size')
    submit = SubmitField('Save')

    wycinek = BooleanField('Newsletter')
    cnfrnce = BooleanField('Conferences')
    anteomnia = BooleanField('Ante Omnia')
    fotki = BooleanField('Zdjęcia')
    fszysko = BooleanField('Fszysko')

    rodo = BooleanField('rodo_placeholder')

    def __init__(self, original_studentid, *args, **kwargs):
        super(EditForm, self).__init__(*args, **kwargs)
        self.original_studentid = original_studentid

    def validate_studentid(self, studentid):
        if studentid.data != self.original_studentid:
            fellow = Fellow.query.filter_by(studentid=self.studentid.data).first()
            if fellow is not None:
                raise ValidationError('This id number is already in the database.')

class ViewForm(FlaskForm):
    activate = SubmitField('Activate')
    deactivate = SubmitField('Deactivate')

class PanelForm(FlaskForm):
    search = StringField('Search', validators=[Optional()])
    active = BooleanField('Aktywni')
    submit = SubmitField('')
"""
