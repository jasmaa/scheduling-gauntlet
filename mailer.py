import os
import sendgrid
from sendgrid.helpers.mail import *

sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')


def send(to: str, subject: str, body: str):
    """Sends email
    """
    from_email = Email(SENDER_EMAIL)
    to_email = To(to)
    content = Content("text/plain", body)
    mail = Mail(from_email, to_email, subject, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    return response
