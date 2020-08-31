import datetime

from flask import render_template, flash, redirect, url_for
from flask_login import login_required

from lada import db
from lada.article import bp
from lada.article.forms import ArticleForm, IndexForm
from lada.models import Article, Tag
from lada.fellow.board import board_required

@bp.route('/', methods=['GET', 'POST'])
def index():
  return render_template('article/index.html', articles=Article.query.all())

@bp.route('/new', methods=['GET', 'POST'])
@board_required(['secret',])
@login_required
def new():
  form = ArticleForm()
  if form.validate_on_submit():
    article = Article(title=form.title.data, body=form.body.data)
    article.posted = datetime.datetime.utcnow()
    #article.tags
    db.session.add(article)
    db.session.commit()
    flash('Article posted successfully.')
    return redirect(url_for('article.index'))
  return render_template('article/new.html', form=form)

@bp.route('/edit', methods=['GET', 'POST'])
@board_required(['secret',])
@login_required
def edit():
  return render_template('article/edit.html')

@bp.route('/view/<id>')
def view(id):
  article = Article.query.filter_by(id=id).first_or_404()
  return render_template('article/view.html', article=article)
