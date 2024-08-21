from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import MAX_LENGTH_CHAR, MAX_LENGTH_CHAR_BIO, MAX_LENGTH_MAIL


class CustomUser(AbstractUser):
    """Кастомная модель пользователя."""

    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    USER_ROLES = [
        (USER, 'user'),
        (MODERATOR, 'moderator'),
        (ADMIN, 'admin'),
    ]

    username = models.CharField(
        'Логин',
        max_length=MAX_LENGTH_CHAR,
        unique=True
    )
    email = models.EmailField('Почта', max_length=MAX_LENGTH_MAIL, unique=True)
    first_name = models.CharField(
        'Имя',
        max_length=MAX_LENGTH_CHAR,
        blank=True
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_LENGTH_CHAR,
        blank=True
    )
    bio = models.CharField(
        'Биография',
        max_length=MAX_LENGTH_CHAR_BIO,
        blank=True
    )
    role = models.CharField(
        'Статус',
        max_length=MAX_LENGTH_CHAR // 3,
        blank=False,
        choices=USER_ROLES,
        default='user'
    )
    confirmation_code = models.CharField(
        verbose_name='Код подтверждения',
        max_length=MAX_LENGTH_CHAR
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_staff

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR
