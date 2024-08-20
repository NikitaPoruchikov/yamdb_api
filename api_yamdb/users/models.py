from django.contrib.auth.models import AbstractUser
from django.db import models


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

    username = models.CharField('Логин', max_length=150, unique=True)
    email = models.EmailField('Почта', max_length=254, unique=True)
    first_name = models.CharField('Имя', max_length=150, blank=True)
    last_name = models.CharField('Фамилия', max_length=150, blank=True)
    bio = models.CharField('Биография', max_length=256, blank=True)
    role = models.CharField(
        'Статус',
        max_length=50,
        blank=False,
        choices=USER_ROLES,
        default='user'
    )
    confirmation_code = models.CharField(
        verbose_name='Код подтверждения', max_length=150
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
