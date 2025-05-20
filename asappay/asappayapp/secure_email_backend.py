# secure_email_backend.py

import smtplib
import ssl
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import sanitize_address

class SecureSMTPEmailBackend(BaseEmailBackend):
    def __init__(self, host=None, port=None, username=None, password=None,
                 use_ssl=True, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently)
        self.host = host or 'smtp.example.com'
        self.port = port or 465
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.connection = None

    def open(self):
        if self.connection:
            return False
        try:
            context = ssl.create_default_context()
            self.connection = smtplib.SMTP_SSL(self.host, self.port, context=context)
            self.connection.login(self.username, self.password)
        except Exception as e:
            if not self.fail_silently:
                raise
            self.connection = None
        return True

    def close(self):
        if self.connection:
            try:
                self.connection.quit()
            except Exception:
                if not self.fail_silently:
                    raise
            finally:
                self.connection = None

    def send_messages(self, email_messages):
        if not email_messages:
            return 0
        self.open()
        if not self.connection:
            return 0

        num_sent = 0
        for message in email_messages:
            try:
                from_email = sanitize_address(message.from_email, message.encoding)
                recipients = [sanitize_address(addr, message.encoding) for addr in message.recipients()]
                self.connection.sendmail(from_email, recipients, message.message().as_string())
                num_sent += 1
            except Exception:
                if not self.fail_silently:
                    raise
        self.close()
        return num_sent
