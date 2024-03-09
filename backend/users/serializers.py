from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'password',
            'first_name',
            'last_name',
        ]
        read_only_fields = ['id']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    model = User

    current_password = serializers.CharField(
        required=True,
        max_length=settings.PASSWORD_MAX_LEN,
    )
    new_password = serializers.CharField(
        required=True,
        max_length=settings.PASSWORD_MAX_LEN,
    )
