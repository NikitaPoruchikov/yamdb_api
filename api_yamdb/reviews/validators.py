from datetime import date

from django.core.validators import BaseValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class PastOrPresentYearValidator(BaseValidator):
    message = _(
        'Ensure title`s year is less than or equal to %(limit_value)s.'
    )
    code = 'past_or_present_year'

    def compare(self, a):
        return a > date.today().year
