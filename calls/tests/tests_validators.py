import unittest
from calls.validators import validate_phone_number
from django.core.exceptions import ValidationError


class TestValidatePhoneNumber(unittest.TestCase):
    def test_valid_phone_number(self):
        self.assertEqual(validate_phone_number('41987654321'), True)
        self.assertEqual(validate_phone_number('4187654321'), True)
        self.assertEqual(validate_phone_number('41888888888'), True)

    def test_invalid_phone_number(self):
        self.assertRaises(ValidationError, validate_phone_number, 'abcdefghi')
        self.assertRaises(ValidationError, validate_phone_number, '123456')
