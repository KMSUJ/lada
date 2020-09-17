from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, HiddenField, SubmitField
from flask_pagedown.fields import PageDownField
from wtforms.validators import DataRequired

class ArticleForm(FlaskForm):
  title = StringField('Title', validators=[DataRequired()])
  tags = HiddenField('Tags')
  taginput = StringField('Tags')
  body = PageDownField('Body', validators=[DataRequired()])
  submit = SubmitField('Post')

  wycinek = BooleanField('Newsletter')
  cnfrnce = BooleanField('Conferences')
  anteomnia = BooleanField('Ante Omnia')
  fotki = BooleanField('Zdjecia')
  fszysko = BooleanField('Wszystko', default=True)

class DeleteForm(FlaskForm):
  delete = SubmitField('delete')
