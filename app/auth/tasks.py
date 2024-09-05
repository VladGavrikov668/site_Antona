from celery import Celery
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

celery_app = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "dogweb20214@gmail.com"
SMTP_PASSWORD = "rmow ovag atij fxdt"


@celery_app.task
def send_verification_email(email: str, verification_link: str):
    """Отправляет письмо с подтверждением аккаунта"""
    message = MIMEMultipart()
    message["From"] = SMTP_USER
    message["To"] = email
    message["Subject"] = "Подтверждение аккаунта"
    body = f"Пожалуйста, подтвердите ваш аккаунт, перейдя по следующей ссылке: {verification_link}"
    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, email, message.as_string())


@celery_app.task
def send_password(email: str, reset_link: str):
    """Отправляет письмо с сбросом пароля"""
    message = MIMEMultipart()
    message["From"] = SMTP_USER
    message["To"] = email
    message["Subject"] = "Сброс пароля"
    body = f"Пожалуйста, сбросьте пароль, перейдя по следующей ссылке: {reset_link}"
    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, email, message.as_string())
