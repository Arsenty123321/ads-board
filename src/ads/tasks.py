from celery import shared_task
from django.core.mail import send_mail

from config.settings import EMAIL_HOST_USER, FRONTEND_SITE_URL


@shared_task
def send_feedback_notification_email(ad_title, ad_owner_email, feedback_owner_email, feedback_text,
                                     feedback_created_at):
    """Задача Celery для отправки уведомления о новом отзыве."""
    subject = f'Новый отзыв на ваше объявление "{ad_title}"'
    message = (f'Пользователь {feedback_owner_email} оставил отзыв на ваше объявление "{ad_title}":\n\n'
               f'{feedback_text}\n\n'
               f'Дата отзыва: {feedback_created_at}\n\n'
               f'Подробности на сайте: {FRONTEND_SITE_URL}')

    send_mail(subject, message, EMAIL_HOST_USER, [ad_owner_email], fail_silently=False)
