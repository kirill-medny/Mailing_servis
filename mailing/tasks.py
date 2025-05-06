import logging

from apscheduler.schedulers.background import BackgroundScheduler
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from mailing.models import Client, Mailing, MailingAttempt

logger = logging.getLogger(__name__)


@shared_task(bind=True, retry_backoff=True)
def send_mailing_task(self, mailing_id):
    """
    Рассылает электронные письма клиентам из списка рассылки.
    """
    mailing = Mailing.objects.get(pk=mailing_id)

    # Проверяем время отправки
    if mailing.status == "completed":
        logger.info(f"Mailing {mailing.pk} is already completed.")
        return

    # Привлекаем клиентов для рассылки
    clients = mailing.clients.all()

    for client in clients:
        try:
            send_mail(
                mailing.message.subject,
                mailing.message.body,
                settings.EMAIL_HOST_USER,  # Отправляем письмо
                [client.email],  # Электронное письмо получателя
                fail_silently=False,
            )
            # Запишите успешную попытку
            MailingAttempt.objects.create(
                mailing=mailing,
                status="success",
                server_response="Email sent successfully",
            )
            logger.info(f"Sent email to {client.email} for mailing {mailing.pk}")

        except Exception as e:
            # Запишите неудачную попытку
            MailingAttempt.objects.create(
                mailing=mailing, status="failure", server_response=str(e)
            )
            logger.error(
                f"Failed to send email to {client.email} for mailing {mailing.pk}: {e}"
            )
            raise self.retry(exc=e, countdown=60)  # Повторите попытку через 60 секунд

    # При необходимости обновите статус рассылки
    mailing.status = "completed"
    mailing.save()
    logger.info(f"Mailing {mailing.pk} completed.")


def mailing_scheduler():

    scheduler = BackgroundScheduler(settings.SCHEDULER_CONFIG)
    scheduler.start()

    mailings = Mailing.objects.filter(status="created")
    for mailing in mailings:

        # Проверка времени отправки
        if mailing.status == "completed":
            logger.info(f"Mailing {mailing.pk} is already completed.")
            return

        if mailing.status == "running":
            logger.info(f"Mailing {mailing.pk} is running.")
            return

        scheduler.add_job(
            send_mailing_task,
            "interval",
            minutes=1,  # Запускать каждую минуту
            start_date=mailing.start_time,
            end_date=mailing.end_time,
            args=[mailing.pk],
            id=f"mailing_{mailing.pk}",  # Уникальный ID для каждой рассылки
            replace_existing=True,  # Перезаписывать задачу, если она уже существует
        )


from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Mailing)
def mailing_post_save(sender, instance, created, **kwargs):
    if created:
        mailing_scheduler()
