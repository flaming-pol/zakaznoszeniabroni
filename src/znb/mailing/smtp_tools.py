import logging
import smtplib
import ssl

from email.message import EmailMessage
from email.utils import formataddr, formatdate, make_msgid
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, PackageLoader
from tenacity import after_log, retry, stop_after_attempt, wait_fixed


environment = Environment(loader=PackageLoader("znb.mailing", "templates"))


class SmtpWrapper:
    def __init__(self, host: str, port: int, tls_support: bool = False,
                 ssl_support: bool = False, user: str = None, passwd: str = None):
        self.host = host
        self.port = port
        self.server = None
        self.reconnects = 0
        self.tls = tls_support
        self.ssl = ssl_support
        self.user = user
        self.passwd = passwd

    def __del__(self):
        if self.server:
            try:
                self.server.quit()
            except smtplib.SMTPServerDisconnected:
                pass

    def authenticate(self):
        if self.tls is True:
            self.server.ehlo()
            self.server.starttls()
        if self.user and self.passwd:
            self.server.login(self.user, self.passwd)

    def connect(self):
        if not self.server:
            if self.ssl is True:
                self.context = ssl.create_default_context()
                self.server = smtplib.SMTP_SSL(self.host, self.port, self.context)
            else:
                self.server = smtplib.SMTP(self.host, self.port)
            self.authenticate()

    @retry(
        stop=stop_after_attempt(10),
        wait=wait_fixed(1),
        after=after_log(logging.getLogger(), logging.WARN),
        reraise=True,
    )
    def send_mail(self, msg: EmailMessage):
        self.connect()
        try:
            self.server.send_message(msg)
        except (smtplib.SMTPServerDisconnected, smtplib.SMTPConnectError) as e:
            self.server.connect(self.host, self.port)
            self.authenticate()
            self.reconnects += 1
            raise e


# def notification_mail_render(destination_email: str, source_email: str, subject: str,
#                              date: str, number: int, year: int, pdf_url: str,
#                              unregister_key: str,
#                              reply_email: str = None) -> MIMEMultipart:
#     message = MIMEMultipart("alternative")
#     message["To"] = destination_email
#     message["From"] = source_email
#     message["Subject"] = subject
#     if reply_email:
#         message["Reply-To"] = reply_email
#
#     template_html = environment.get_template("basic_html.j2")
#     template_plain = environment.get_template("basic_plaintext.j2")
#
#     content_html = template_html.render(
#         date=date,
#         number=number,
#         year=year,
#         pdf_url=pdf_url,
#         unregister_key=unregister_key,
#     )
#     content_plaintext = template_plain.render(
#         date=date,
#         number=number,
#         year=year,
#         pdf_url=pdf_url,
#         unregister_key=unregister_key,
#     )
#     part1 = MIMEText(content_html, "html")
#     part2 = MIMEText(content_plaintext, "plain", "utf-8")
#     message.attach(part1)
#     message.attach(part2)
#     return message


def notification_mail_render(destination_email: str, source_email: str, subject: str,
                             date: str, number: int, year: int, pdf_url: str,
                             unregister_key: str,
                             reply_email: str = None) -> EmailMessage:
    message = EmailMessage()
    message['Date'] = formatdate()
    message['Message-ID'] = make_msgid(domain=source_email.split('@')[1])
    message["To"] = destination_email
    message["From"] = formataddr(("ZakazyNoszeniaBroni.pl", source_email))
    message["Subject"] = subject
    if reply_email:
        message["Reply-To"] = reply_email

    template_html = environment.get_template("basic_html.j2")

    content_html = template_html.render(
        date=date,
        number=number,
        year=year,
        pdf_url=pdf_url,
        unregister_key=unregister_key,
    )
    message.set_content(content_html, subtype="html")
    return message


# def confirmation_mail_render(destination_email: str, source_email: str,
#                              subject: str, confirmation_string: str,
#                              reply_email: str = None) -> MIMEMultipart:
#     message = MIMEMultipart("alternative")
#     message["To"] = destination_email
#     message["From"] = source_email
#     message["Subject"] = subject
#     if reply_email:
#         message["Reply-To"] = reply_email
#
#     template_html = environment.get_template("confirmation_html.j2")
#     template_plain = environment.get_template("confirmation_plain.j2")
#
#     content_html = template_html.render(
#         confirmation_string=confirmation_string,
#     )
#     content_plaintext = template_plain.render(
#         confirmation_string=confirmation_string,
#     )
#     part1 = MIMEText(content_html, "html")
#     part2 = MIMEText(content_plaintext, "plain", "utf-8")
#     message.attach(part1)
#     message.attach(part2)
#     return message


def confirmation_mail_render(destination_email: str, source_email: str,
                             subject: str, confirmation_string: str,
                             reply_email: str = None) -> EmailMessage:
    message = EmailMessage()
    message['Date'] = formatdate()
    message['Message-ID'] = make_msgid(domain=source_email.split('@')[1])
    message["To"] = destination_email
    message["From"] = formataddr(("ZakazyNoszeniaBroni.pl", source_email))
    message["Subject"] = subject
    if reply_email:
        message["Reply-To"] = reply_email

    template_html = environment.get_template("confirmation_html.j2")

    content_html = template_html.render(
        confirmation_string=confirmation_string,
    )
    message.set_content(content_html, subtype="html")
    return message
