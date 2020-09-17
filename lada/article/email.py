from flask import render_template, current_app

from lada.email import send_email
from lada.models import Fellow

def checked_mail_groups(form):
  _dict = {'wycinek':form.wycinek.data, 'cnfrnce':form.cnfrnce.data, 'anteomnia':form.wycinek.data, 'fotki':form.wycinek.data, 'fszysko':form.wycinek.data, }
  return (key for key in _dict if _dict[key])

def email_article(form):
  send_article_email(title=form.title.data.title(), 
      body=form.body.data, 
      recipients = (fellow.email for fellow in Fellow.query.all() if any(fellow.check_newsletter(group) for group in checked_mail_groups(form))))

def send_article_email(title, body, recipients):
  send_email(f'[KMSuj] {title}', 
      sender='no-reply@kms.uj.edu.pl', 
      recipients=recipients, 
      text_body=render_template('article/email/article.txt', title=title, body=body), 
      html_body=render_template('article/email/article.html', title=title, body=body))
