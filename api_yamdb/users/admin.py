from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Кастомный администратор пользователей Django."""

    model = CustomUser
    ordering = ['email']
