from django.conf import settings
from django.core.mail import send_mail


def send_code_to_mail(email, confirmation_code):
    """Отправка сообщений с кодом подтверждения на почту."""

    send_mail(
        subject='YaMDb Confirmation Code',
        message=f'Ваш проверочный код: {confirmation_code}',
        from_email=settings.EMAIL_SENDER,
        recipient_list=[email],
        fail_silently=False
    )
