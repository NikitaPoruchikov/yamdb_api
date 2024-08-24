
from django.core.exceptions import ValidationError


def validate_username(value):
    if not isinstance(value, str):
        raise ValidationError('Username должен иметь тип str')
    if value.lower() == 'me':
        raise ValidationError('Имя пользователя <me> недопустимо.')
    return value
