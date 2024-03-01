from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class CustomUserManager(UserManager):
    def get_by_natural_key(self, username):
        return self.get(**{self.model.EMAIL_FIELD: username})


class User(AbstractUser):
    """Custom user model."""

    password = models.CharField('Пароль', max_length=settings.PASSWORD_MAX_LEN)

    objects = CustomUserManager()

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
