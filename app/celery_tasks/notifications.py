import logging
import smtplib
from email.header import Header
from email.mime.text import MIMEText

from app.celery_tasks.celery_worker import celery_app
from app.core.config import load_config

logger = logging.getLogger(__name__)

config = load_config()

EMAIL = config.mailing.email
EMAIL_PASSWORD = config.mailing.email_password


@celery_app.task(
    bind=True,
    max_retries=5,
    autoretry_for=(smtplib.SMTPException,),
    retry_backoff=True,
    retry_jitter=True)
def send_email(self, to_email: str, subject: str, body: str):
    """
    Асинхронная задача отправки email через SMTP с защитой от повторной отправки.

    Отправляет простое текстовое письмо с указанным адресатом, темой и телом письма.
    Используется защищённое SSL-соединение и авторизация по логину и паролю приложения.

    Args:
        to_email (str): Email-адрес получателя.
        subject (str): Тема письма.
        body (str): Текст письма (plain text).

    Raises:
        smtplib.SMTPException: Ошибка при подключении к SMTP-серверу или отправке письма.
        Exception: Любая другая ошибка, возникшая во время выполнения задачи.

    Пример:
        send_email.delay("user@example.com", "Уведомление", "Задача успешно выполнена.")
    """
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = EMAIL
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.yandex.ru", 465, timeout=10) as server:
            server.login(EMAIL, EMAIL_PASSWORD)
            server.sendmail(EMAIL, to_email, msg.as_string())
        logger.info(f"✅ Email sent to {to_email}")

    except smtplib.SMTPRecipientsRefused as e:
        logger.error(f"❌ Invalid recipient: {e}")
    except smtplib.SMTPAuthenticationError as e:
        logger.critical(f"❌ SMTP auth error: {e}")
        raise
    except (smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected, smtplib.SMTPDataError, ConnectionError) as e:
        logger.warning(f"🔁 Retryable SMTP error: {e}")
        raise self.retry(exc=e)
    except Exception as e:
        logger.exception(f"❌ Unexpected error, retrying: {e}")
        raise self.retry(exc=e)
