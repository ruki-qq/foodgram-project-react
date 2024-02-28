from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers


User = get_user_model()


class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=settings.USERNAME_MAX_LEN,
        validators=[
            UnicodeUsernameValidator(),
        ],
    )
    email = serializers.EmailField(
        max_length=settings.EMAIL_MAX_LEN,
    )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
        ]


class MyTokenObtainSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=settings.USERNAME_MAX_LEN,
        validators=[UnicodeUsernameValidator()],
    )
    confirmation_code = serializers.CharField()
