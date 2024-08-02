import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import Environment, FileSystemLoader

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_LOGIN = os.getenv("SMTP_LOGIN")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


class Mailer:
    def __init__(self):
        template_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def _render_template(self, template_name, context):
        template = self.env.get_template(template_name)
        return template.render(context)

    def _create_mime_message(self, subject, sender, recipient, html_content):
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender
        message["To"] = recipient
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)
        return message

    def send_email(self, subject, sender, recipient, template_name, context={}):
        html_content = self._render_template(template_name, context)
        mime_message = self._create_mime_message(
            subject, sender, recipient, html_content
        )
        if not SMTP_HOST or not SMTP_PORT:
            raise ValueError("SMTP_HOST and SMTP_PORT must be set")

        with smtplib.SMTP(SMTP_HOST, int(SMTP_PORT)) as server:
            if SMTP_LOGIN and SMTP_PASSWORD:
                server.login(SMTP_LOGIN, SMTP_PASSWORD)

            server.send_message(mime_message)


def get_mailer() -> Mailer:
    return Mailer()
