from flask import render_template, current_app
from lada.email import send_email

def send_password_reset_email(fellow):
  token = fellow.get_password_reset_token()
  send_email(_('[KMSuj] Password Reset'), 
      sender='no-reply@kms.uj.edu.pl', 
      recipients=[user.email], 
      text_body=render_template('email/reset_password.txt', user=user, token=token), 
      html_body=render_template('email/reset_password.html', user=user, token=token))
