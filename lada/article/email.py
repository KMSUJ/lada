from flask import render_template

from lada.constants import *
from lada.email import send_email
from lada.models import Fellow


def checked_mail_groups(form):
    _dict = {
        NEWS_WYCINEK: form.wycinek.data,
        NEWS_CONFERENCE: form.cnfrnce.data,
        NEWS_ANTEOMNIA: form.wycinek.data,
        NEWS_PHOTO: form.wycinek.data,
        NEWS_ALL: form.wycinek.data,
    }
    return (key for key in _dict if _dict[key])


def email_article(form):
    send_article_email(title=form.title.data.title(),
                       body=form.body.data,
                       recipients=(fellow.email for fellow in Fellow.query.all() if
                                   any(fellow.check_newsletter(group) for group in checked_mail_groups(form))))


def send_article_email(title, body, recipients):
    send_email(f'[KMSuj] {title}',
               sender='no-reply@kms.uj.edu.pl',
               recipients=recipients,
               text_body=render_template('article/email/article.txt', title=title, body=body),
               html_body=render_template('article/email/article.html', title=title, body=body))
