from drf_extra_fields.fields import Base64ImageField


class CustomBase64ImageField(Base64ImageField):
    EMPTY_VALUES = ()
