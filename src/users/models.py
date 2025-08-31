import secrets

from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

ROLE_CHOICES = (
    ("user", "user"),
    ("admin", "admin"),
)


class User(AbstractUser):
    """Модель пользователя"""

    username = None
    email = models.EmailField(unique=True, verbose_name="email")
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    last_name = models.CharField(max_length=50, verbose_name="Фамилия", blank=True, null=True)
    phone = PhoneNumberField(verbose_name="Телефон для связи", blank=True, null=True)
    image = models.ImageField(upload_to="users_avatars/", verbose_name="Аватар", blank=True, null=True)

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="user", verbose_name="Роль пользователя")
    activation_code = models.CharField(max_length=32, verbose_name="activation_code", blank=True, null=True)
    is_active = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def generate_activation_code(self):
        self.activation_code = secrets.token_hex(16)

    def __str__(self):
        return f"{self.email}, {self.role}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("id", "role")
