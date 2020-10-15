import logging

import lada.models

from flask_mail import Message

from lada import mail
from lada.multithreading import run_async

log = logging.getLogger(__name__)


def _send_sync_email(app, message):
    with app.app_context():
        log.debug(f"Sending e-mail message to {message.recipients}: {message.subject}")

        mail.send(message)


def process_recipient(recipient):
    if isinstance(recipient, str) or isinstance(recipient, tuple):
        return recipient
    return f"{recipient.name} {recipient.surname}", recipient.email


def send_email(subject, recipients, text_body, html_body=None, sender=None, reply_to=None):
    if reply_to is None and sender is None:
        reply_to = ('Koło Matematyków Studentów UJ', 'kmsuj7@gmail.com')

    sender = sender or ('Koło Matematyków Studentów UJ', 'kmsuj7@gmail.com')

    recipients = list(map(process_recipient, recipients))

    msg = Message(
        subject=f"[KMSuj] {subject}",
        recipients=recipients,
        body=text_body,
        html=html_body,
        sender=sender,
        reply_to=reply_to
    )
    run_async(_send_sync_email, message=msg, deamon=False)
