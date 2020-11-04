import logging

from flask import render_template

from lada.email import send_email

log = logging.getLogger(__name__)


def send_verification_email(fellow):
    log.info(f"Sending verification email to {fellow}")
    token = fellow.get_verification_token()
    send_email('Email Verification',
               recipients=[fellow],
               text_body=render_template('fellow/email/verification.txt', fellow=fellow, token=token),
               html_body=render_template('fellow/email/verification.html', fellow=fellow, token=token),
               )


def send_password_reset_email(fellow):
    log.info(f"Sending password reset email to {fellow}")
    token = fellow.get_password_reset_token()
    send_email('Password Reset',
               recipients=[fellow],
               text_body=render_template('fellow/email/reset_password.txt', fellow=fellow, token=token),
               html_body=render_template('fellow/email/reset_password.html', fellow=fellow, token=token),
               )

# delete later
def send_import_email(fellow):
  log.info(f"Sending welcome import email to {fellow}")
  verification_token = fellow.get_verification_token()
  password_token = fellow.get_password_reset_token()
  send_email('Database Migration',
             recipients=[fellow],
             text_body=render_template('fellow/email/import.txt', fellow=fellow, verification_token=verification_token, password_token=password_token),
             html_body=render_template('fellow/email/import.html', fellow=fellow, verification_token=verification_token, password_token=password_token),
             )
# enddelete
