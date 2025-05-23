from .celery_worker import celery_app


@celery_app.task
def send_email_mock(to_email: str, subject: str):
    print(f"📧 Email to {to_email} with subject '{subject}'")


@celery_app.task
def send_webhook_mock(url: str, payload: dict):
    print(f"🌐 Webhook sent to {url} with payload {payload}")
