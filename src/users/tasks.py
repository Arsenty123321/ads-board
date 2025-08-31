from celery import shared_task
from django.core.mail import send_mail

from config.settings import EMAIL_HOST_USER


@shared_task
def send_activation_email(user_email, activation_url):
    """Задача для отправки ссылки активации на email."""

    send_mail(
        'Подтверждение регистрации на сайте "Доска объявлений"',
        f'Для подтверждения регистрации перейдите по ссылке: {activation_url}',
        EMAIL_HOST_USER,
        [user_email],
        fail_silently=False
    )


@shared_task
def send_password_reset_link_email(user_email, reset_link):
    """Задача для отправки ссылки-токена на сброс пароля."""

    send_mail(
        'Сброс пароля на сайте "Доска объявлений"',
        f'Для сброса пароля перейдите по ссылке: {reset_link}',
        EMAIL_HOST_USER,
        [user_email],
        fail_silently=False,
    )
