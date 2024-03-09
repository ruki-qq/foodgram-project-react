from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField('Название', max_length=settings.TAG_NAME_MAX_LEN)
    color = models.CharField(
        'Цвет',
        max_length=settings.TAG_COLOR_MAX_LEN,
        blank=True,
        null=True,
    )
    slug = models.SlugField(
        'Слаг',
        max_length=200,
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=settings.ING_NAME_MAX_LEN)
    measurement_unit = models.CharField(
        'Единица измерения', max_length=settings.ING_MES_MAX_LEN
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = models.CharField(
        'Название',
        max_length=settings.RECIPE_NAME_MAX_LEN,
    )
    text = models.TextField('Описание')
    cooking_time = models.PositiveSmallIntegerField(
        default=5,
        validators=[MinValueValidator(1)],
    )
    image = models.ImageField(upload_to='api/imgs/')
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        verbose_name='Ингредиенты',
    )
    favorites = models.ManyToManyField(
        User,
        related_name='favorites',
        verbose_name='Избранное',
    )

    def __str__(self):
        return self.name
