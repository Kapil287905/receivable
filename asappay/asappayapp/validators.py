import re
from django.core.exceptions import ValidationError
from django.core.validators import validate_email as django_validate_email

def validate_pan(value):
    pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]$'
    if not re.fullmatch(pattern, value):
        raise ValidationError("Invalid PAN number format (e.g., ABCDE1234F)")
    
def validate_phone(phone):
    pattern = r'^[6-9]\d{9}$'  # Indian 10-digit number starting with 6-9
    if not re.fullmatch(pattern, phone):
        raise ValidationError("Invalid phone number. Enter a valid 10-digit Indian mobile number.")

def validate_email(email):
    try:
        django_validate_email(email)
    except ValidationError:
        raise ValidationError("Invalid email address.")