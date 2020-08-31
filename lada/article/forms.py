from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class ArticleForm(FlaskForm):
  title = StringField('Title', validators=[DataRequired()])
  tags = StringField('Tags')
  body = StringField('Body', validators=[DataRequired()])
  submit = SubmitField()

class IndexForm(FlaskForm):
  pass
