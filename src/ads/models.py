from django.db import models

from users.models import User


class Advertisement(models.Model):
    """Модель объявления"""

    title = models.CharField(max_length=255, verbose_name="Название объявления")
    price = models.PositiveIntegerField(default=1, verbose_name="Стоимость товара/услуги")
    description = models.TextField(verbose_name="Описание")
    author = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="owner", verbose_name="Автор объявления",
                               blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True, verbose_name="Дата создания объявления", blank=True, null=True)

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        ordering = ("-created_at", "id")

    def __str__(self):
        return f"{self.title}, {self.created_at}, {self.author}, {self.price}"
