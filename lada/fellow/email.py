from flask import render_template, current_app
from lada.email import send_email

def send_password_reset_email(fellow):
  token = fellow.get_password_reset_token()
  send_email('[KMSuj] Password Reset', 
      sender='no-reply@kms.uj.edu.pl', 
      recipients=[fellow.email], 
      text_body=render_template('fellow/email/reset_password.txt', fellow=fellow, token=token), 
      html_body=render_template('fellow/email/reset_password.html', fellow=fellow, token=token))
