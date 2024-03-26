from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework.serializers import (
    ValidationError as SerializerValidationError,
)


def validate_pwd(password):
    """If password is valid returns it.
    If password is invalid raises SerializerValidationError.
    """

    try:
        validate_password(password)
    except ValidationError as err:
        raise SerializerValidationError(err.messages)
    return password
