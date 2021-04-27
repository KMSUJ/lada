from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Optional, Email, EqualTo

from lada.models import Fellow

# rodo_cyrograf = 'Wyrażam zgodę na przetwarzanie moich danych osobowych w zakresie ……………………… w celu ……………………………………, zgodnie z Rozporządzeniem Parlamentu Europejskiego i Rady (UE) 2016/679 z dnia 27 kwietnia 2016 r. (ogólne rozporządzenie o ochronie danych) oraz zgodnie z klauzulą informacyjną dołączoną do mojej zgody.'
rodo_cyrograf = 'Wyrażam zgodę na przetwarzanie moich danych osobowych, zgodnie z Rozporządzeniem Parlamentu Europejskiego i Rady (UE) 2016/679 z dnia 27 kwietnia 2016 r. (ogólne rozporządzenie o ochronie danych) oraz zgodnie z klauzulą informacyjną dołączoną do mojej zgody.'

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Name', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    studentid = IntegerField('Student Id', validators=[Optional()])
    password = PasswordField('Password', validators=[DataRequired()])
    repassword = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    rodo = BooleanField(rodo_cyrograf)

    def validate_email(self, email):
        fellow = Fellow.query.filter_by(email=email.data).first()
        if fellow is not None:
            raise ValidationError('This email adress is already in the database.')

    def validate_studentid(self, studentid):
        fellow = Fellow.query.filter_by(studentid=studentid.data).first()
        if fellow is not None:
            raise ValidationError('This id number is already in the database.')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Reset')


class PasswordResetForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    repassword = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset')


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

    rodo = BooleanField(rodo_cyrograf)

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
