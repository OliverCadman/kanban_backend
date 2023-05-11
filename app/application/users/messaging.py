from application.mail import mailing
from flask_mail import Message
import os

def send_email(to, subject, url, template=None):
    msg = Message(
        subject,
        recipients=[to],
        body=f"Visit this link to confirm your email: {url}",
        sender=os.environ.get('MAIL_DEFAULT_SENDER')
    )

    mailing_attempt = mailing.send(msg)
