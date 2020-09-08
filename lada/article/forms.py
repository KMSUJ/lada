from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, SubmitField
from wtforms.validators import DataRequired

class ArticleForm(FlaskForm):
  title = StringField('Title', validators=[DataRequired()])
  tags = HiddenField('Tags')
  taginput = StringField('Tags')
  body = StringField('Body', validators=[DataRequired()])
  submit = SubmitField('Post')

class IndexForm(FlaskForm):
  pass

class DeleteForm(FlaskForm):
  delete = SubmitField('delete')
