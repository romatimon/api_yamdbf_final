from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

from api.v1.validators import username_validator
from api_yamdb.settings import MAX_LENGTH_EMAIL, MAX_LENGTH_USERNAME


class User(AbstractUser):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
    ROLE_CHOICES = (
        (USER, "Пользователь"),
        (MODERATOR, "Модератор"),
        (ADMIN, "Администратор"),
    )

    username = models.CharField(
        "Имя пользователя",
        max_length=MAX_LENGTH_USERNAME,
        unique=True,
        validators=[username_validator, RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Имя пользователя содержит недопустимый символ'
        )]
    )
    email = models.EmailField(
        max_length=MAX_LENGTH_EMAIL,
        unique=True,
        verbose_name="Email:",
        help_text="Укажите действующий Email.",
    )
    bio = models.TextField(
        null=True,
        verbose_name="О себе:",
        help_text="Напишите немного о себе.",
    )
    role = models.CharField(
        "Роль",
        max_length=max(len(role) for role, _ in ROLE_CHOICES),
        choices=ROLE_CHOICES,
        default=USER,
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователь"

    def __str__(self):
        return f"username: {self.username}, email: {self.email}"

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser or self.is_staff
