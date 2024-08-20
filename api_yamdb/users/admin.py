from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Кастомный администратор пользователей Django"""

    add_form = CustomUserCreationForm
    model = CustomUser
    ordering = ('email',)
