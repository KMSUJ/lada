import datetime

import flask_featureflags as feature
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import login_required
from sqlalchemy import desc

from lada import db
from lada.article import bp
from lada.article.email import email_article
from lada.article.forms import ArticleForm, DeleteForm
from lada.fellow.board import board_required
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
@board_required(['secret', ])
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
        email_article(form)
        flash('Article posted successfully.')
        return redirect(url_for('article.index'))
    return render_template('article/new.html', form=form, label="Nowy Artykuł")


# delete later
import random

heading = "Lorem ipsum dolor sit amet."
body = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque hendrerit eget tortor eget accumsan. In egestas, velit at semper accumsan, enim mauris blandit tortor, feugiat tempor augue neque vel tellus. Suspendisse tempor erat sed condimentum tincidunt. Aliquam eu sem congue, interdum eros quis, efficitur massa. Ut ut pellentesque est. Aliquam interdum, mi at ornare malesuada, turpis turpis bibendum mi, non maximus sem neque rhoncus ex. Donec euismod felis quis viverra eleifend. Phasellus suscipit fringilla ex, in volutpat mauris lobortis et. Sed sed elementum erat. Cras pellentesque neque quis odio ultrices, eget maximus magna vehicula. Donec vulputate maximus felis at hendrerit. Integer dapibus metus a suscipit malesuada. Etiam id urna feugiat tellus gravida pellentesque vel et dui. In sollicitudin, mi sollicitudin dapibus dictum, felis nulla gravida leo, vel ornare eros urna ac dolor. Suspendisse ac feugiat ante. Sed pulvinar porta nibh at bibendum. Pellentesque hendrerit pharetra lacus ut faucibus. Nulla fringilla nulla in massa feugiat, sit amet porttitor purus vestibulum. Aliquam erat volutpat. Nullam aliquam, libero id cursus congue, eros eros laoreet turpis, vitae mattis risus nunc sed odio. Proin maximus, augue quis aliquet laoreet, massa dui suscipit nisi, vel consequat ipsum odio sed eros. Duis facilisis et erat ac rhoncus. Nulla ac molestie mi. Nulla pellentesque nec nisi sit amet blandit. Vivamus ligula mauris, lacinia ut tincidunt quis, condimentum sit amet sem. Integer ut est velit. Curabitur ante nisi, lobortis non lobortis vitae, facilisis eget metus. Fusce cursus lorem massa, nec mollis leo elementum a. Vivamus placerat mauris ipsum, in pulvinar est commodo sit amet. In sed diam vitae felis ullamcorper laoreet facilisis vitae nulla. Sed tempor euismod dui. Aenean gravida ac leo non suscipit. Pellentesque porta a nisi vitae mattis. Etiam ultricies, arcu non feugiat tincidunt, lectus mauris aliquet arcu, eget fringilla nulla arcu eget quam. Suspendisse commodo varius nulla, sit amet lacinia libero placerat in. Pellentesque ullamcorper aliquam odio. Curabitur sed hendrerit mi, ac semper nibh. Vivamus non dapibus urna, quis porttitor ligula. Integer at dolor nisl. Curabitur enim mauris, dictum nec arcu vitae, pellentesque ullamcorper orci. Phasellus sed nulla ipsum. Sed rutrum tempus lectus eu posuere. Vivamus sed lorem felis. Vivamus vestibulum justo ac eleifend pulvinar. Sed venenatis risus sollicitudin urna pellentesque, et varius purus facilisis. 
"""
tags = "lorem ipsum dolor sit amet"


@bp.route('/seeddb')
@feature.is_active_feature('demo')
def seeddb():
    for x in range(72):
        heading_parts = heading.split(" ")
        random.shuffle(heading_parts)
        content_parts = body.split(" ")
        random.shuffle(content_parts)
        tag_parts = tags.split(" ")
        random.shuffle(tag_parts)
        article = Article(title=" ".join(heading_parts), body=" ".join(content_parts))
        article.posted = datetime.datetime.utcnow()
        db.session.add(article)
        for value in tag_parts[:3]:
            tag = Tag.query.filter_by(line=value).first()
            if tag is None:
                tag = Tag(line=value)
                db.session.add(tag)
            article.add_tag(tag)
    db.session.commit()
    return redirect(url_for('article.index'))


# enddelete

@bp.route('/edit/<id>', methods=['GET', 'POST'])
@board_required(['secret', ])
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
