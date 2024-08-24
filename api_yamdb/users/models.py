from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .constants import MAX_LENGTH_CHAR, MAX_LENGTH_CHAR_BIO, MAX_LENGTH_MAIL
from .validators import validate_username


class CustomUser(AbstractUser):
    """Кастомная модель пользователя."""

    class UserGrade(models.TextChoices):
        USER = 'user', _('User')
        MODERATOR = 'moderator', _('Moderator')
        ADMIN = 'admin', _('Admin')

    username = models.CharField(
        'Логин',
        max_length=MAX_LENGTH_CHAR,
        unique=True,
        validators=(validate_username, UnicodeUsernameValidator())
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
        choices=UserGrade.choices,
        default=UserGrade.USER,
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
        return self.role == self.UserGrade.ADMIN or self.is_staff

    @property
    def is_moderator(self):
        return self.role == self.UserGrade.MODERATOR
