from django.db import models
from django.utils import timezone

from users.models import User


class Advertisement(models.Model):
    """Модель объявления."""

    title = models.CharField(max_length=64, verbose_name="Название объявления")
    price = models.PositiveIntegerField(default=1, verbose_name="Стоимость товара/услуги")
    description = models.TextField(max_length=8192, verbose_name="Описание")
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="ads_owner",
                              verbose_name="Владелец объявления", blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True, verbose_name="Дата создания объявления", blank=True, null=True)

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        ordering = ("-created_at", "id")

    def __str__(self):
        return f"{self.title}, {self.created_at}, {self.owner}, {self.price}"


class Feedback(models.Model):
    """Модель отзыва."""

    text = models.TextField(max_length=1024, verbose_name="Текст отзыва")
    owner = models.ForeignKey(User, related_name="user_feedback", on_delete=models.CASCADE,
                              verbose_name="Владелец отзыва", blank=True, null=True)
    ad = models.ForeignKey(Advertisement, related_name="ad_feedback", on_delete=models.CASCADE,
                           verbose_name="Объявление, под которым оставлен отзыв", blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата и время отзыва")

    def __str__(self):
        return f"Отзыв от {self.owner}, создан: {self.created_at}"

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ("owner", "created_at")
