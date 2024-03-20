from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class CustomUserManager(UserManager):
    """Custom user manager."""

    def get_by_natural_key(self, username):
        return self.get(**{self.model.EMAIL_FIELD: username})


class User(AbstractUser):
    """Custom user model."""

    email = models.EmailField(
        'Электронная почта',
        max_length=settings.EMAIL_MAX_LEN,
        unique=True,
    )

    first_name = models.CharField(
        'Имя',
        max_length=settings.FIRST_NAME_MAX_LEN,
    )

    last_name = models.CharField(
        'Фамилия',
        max_length=settings.LAST_NAME_MAX_LEN,
    )

    password = models.CharField(
        'Пароль',
        max_length=settings.PASSWORD_MAX_LEN,
    )

    followers = models.ManyToManyField(
        'self',
        through='FollowRelationship',
        related_name='following',
        symmetrical=False,
        blank=True,
    )

    objects = CustomUserManager()

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class FollowRelationship(models.Model):
    to_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='+'
    )
    from_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='+'
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                name='%(app_label)s_%(class)s_unique_relationships',
                fields=['from_user', 'to_user'],
            ),
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_prevent_self_follow',
                check=~models.Q(from_user=models.F('to_user')),
            ),
        ]

    def __str__(self):
        return f'Подписка от {self.from_user} на {self.to_user}.'
