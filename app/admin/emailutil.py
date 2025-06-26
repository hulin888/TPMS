from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
from typing import List

conf = ConnectionConfig(
    MAIL_USERNAME = "sdpatil123456",
    MAIL_PASSWORD = "jyoti@patil",
    MAIL_FROM = "sdpatil123456@gmail.com",
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_TLS = True,
    MAIL_SSL = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

async def send_email(subject:str, recipient:List, message:str):
    message = MessageSchema(
        subject = subject,
        recipients = recipient,
        html = message,
        subtype='html',
    )
    fm = FastMail(conf)
    await fm.send_message(message)