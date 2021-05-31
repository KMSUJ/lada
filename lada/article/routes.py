import datetime

import flask_featureflags as feature
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import login_required
from sqlalchemy import desc

from lada import db
from lada.article import bp
from lada.article.forms import ArticleForm, DeleteForm
from lada.constants import *
from lada.models import Article, Tag


@bp.route('/')
@bp.route('/<tagline>')
def index(tagline=None):
    page = request.args.get('page', 1, type=int)
    if tagline is None:
        articles = Article.query.order_by(desc(Article.posted)).paginate(page, current_app.config['ARTICLE_PER_PAGE'],
                                                                         False)
    else:
        articles = Tag.query.filter_by(line=tagline).first().articles.paginate(page,
                                                                               current_app.config['ARTICLE_PER_PAGE'],
                                                                               False)
    return render_template('article/index.html', articles=articles, tagline=tagline)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    form = ArticleForm()
    if form.validate_on_submit():
        article = Article(title=form.title.data, body=form.body.data)
        article.posted = datetime.datetime.utcnow()
        db.session.add(article)
        for value in form.tags.data.split(" "):
            tag = Tag.query.filter_by(line=value).first()
            if tag is None:
                tag = Tag(line=value)
                db.session.add(tag)
            article.add_tag(tag)
        db.session.commit()
        flash('Article posted successfully.')
        return redirect(url_for('article.index'))
    return render_template('article/new.html', form=form, label="Nowy Artykuł")


@bp.route('/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    article = Article.query.filter_by(id=id).first_or_404()
    form = ArticleForm()
    if form.validate_on_submit():
        article.title = form.title.data
        article.body = form.body.data
        article.clear_tags()
        for value in form.tags.data.split(" "):
            tag = Tag.query.filter_by(line=value).first()
            if tag is None:
                tag = Tag(line=value)
                db.session.add(tag)
            article.add_tag(tag)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('article.view', id=id))
    elif request.method == 'GET':
        form.title.data = article.title
        form.body.data = article.body
        form.tags.data = " ".join(value.line for value in article.tags)
    return render_template('article/new.html', form=form, label="Edytuj Artykuł")


@bp.route('/view/<id>', methods=['GET', 'POST'])
def view(id):
    form = DeleteForm()
    article = Article.query.filter_by(id=id).first_or_404()
    if form.validate_on_submit():
        article.clear_tags()
        db.session.delete(article)
        db.session.commit()
        flash('Article deleted successfully.')
        return redirect(url_for('article.index'))
    return render_template('article/view.html', form=form, article=article)
