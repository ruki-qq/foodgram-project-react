from drf_extra_fields.fields import Base64ImageField


class CustomBase64ImageField(Base64ImageField):
    """Custom field to prevent returning None instead of empty string."""

    EMPTY_VALUES = ()
