from colorfield.fields import ColorField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField('Название', max_length=settings.TAG_NAME_MAX_LEN)
    color = ColorField('Цвет', default='#FF0000')
    slug = models.SlugField(
        'Слаг',
        max_length=200,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=settings.ING_NAME_MAX_LEN)
    measurement_unit = models.CharField(
        'Единица измерения', max_length=settings.ING_MES_MAX_LEN
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

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
        'Время приготовления',
        validators=[MinValueValidator(1)],
    )
    image = models.ImageField('Изображение', upload_to='api/imgs/')
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        verbose_name='Ингредиенты',
        through='IngredientQuantity',
    )
    favorites = models.ManyToManyField(
        User,
        related_name='favorites',
        verbose_name='Избранное',
    )
    shopping_cart = models.ManyToManyField(
        User,
        related_name='shopping_cart',
        verbose_name='Корзина покупок',
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientQuantity(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        'Количество',
        default=1,
        validators=[MinValueValidator(1)],
    )

    def __str__(self):
        return (
            f'В рецепте "{self.recipe.__str__()}"'
            f' {self.amount} {self.ingredient.measurement_unit} ингредиента'
            f' {self.ingredient.__str__()}.'
        )
