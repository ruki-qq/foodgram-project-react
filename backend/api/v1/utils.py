from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework.serializers import (
    ValidationError as SerializerValidationError,
)


def validate_pwd(password):
    try:
        validate_password(password)
    except ValidationError as err:
        raise SerializerValidationError(err.messages)
