from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError

from .constants import USERNAME_RESERVED


class CustomUsernameValidator(UnicodeUsernameValidator):

    def __call__(self, value: str) -> None:
        if value == USERNAME_RESERVED:
            raise ValidationError(
                f'You cannot use {USERNAME_RESERVED} for username!'
            )
        return super().__call__(value)
