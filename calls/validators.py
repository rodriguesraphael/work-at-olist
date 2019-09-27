import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


"""
The phone number format is AAXXXXXXXXX, where AA is the area code and XXXXXXXXX 
is the phone number. The area code is always composed of two digits while the 
phone number can be composed of 8 or 9 digits.
"""
PHONE_REGEX = re.compile(r'^[0-9]{2}(?:[0-9]{8}|[0-9]{9})$')


def validate_phone_number(value):
    validate = re.match(PHONE_REGEX, value)
    if validate:
        return True
    else:
        raise ValidationError(
            _('%s is not a valid phone number. '
              'Use AAXXXXXXXXX or AAXXXXXXXX, eg: 41998765432' % value),
        )
