from flask_pagedown.fields import PageDownField
from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, SubmitField
from wtforms.validators import DataRequired


class ArticleForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    tags = HiddenField('Tags')
    taginput = StringField('Tags')
    body = PageDownField('Body', validators=[DataRequired()])
    submit = SubmitField('Post')


class DeleteForm(FlaskForm):
    delete = SubmitField('delete')
