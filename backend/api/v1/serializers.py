from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import F
from django.db.transaction import atomic
from rest_framework import serializers

from api.v1.mixins import CustomBase64ImageField
from api.v1.utils import validate_pwd
from recipes.models import Ingredient, IngredientQuantity, Recipe, Tag

User = get_user_model()


class IngredientsField(serializers.Field):
    default_error_messages = {
        'empty_list': 'Не выбрано ни одного ингредиента.',
        'incorrect_type': (
            'Неверный тип ингредиента, ожидается: dict, получен: {ing_type}.'
        ),
        'incorrect_keys': (
            'Неверные ключи словаря, ожидаются: {id, amount}, получены:'
            ' {ing_keys}.'
        ),
        'ing_not_exist': 'Ингредиент с id {ing_id} не существует.',
        'amount_less_than_1': (
            'Количество ингредиента {ing_id} не может быть меньше 1.'
        ),
        'ing_repeat': 'Ингредиент {ing_id} передан больше 1 раза.',
    }

    def to_representation(self, ingredients):
        return ingredients.values().annotate(
            amount=F('ingredientquantity__amount')
        )

    def to_internal_value(self, ingredients):
        if not ingredients:
            self.fail('empty_list')

        used_ingredients = set()
        for ingredient in ingredients:
            if not isinstance(ingredient, dict):
                self.fail('incorrect_type', ing_type=type(ingredient))

            if set(ingredient.keys()) != {'id', 'amount'}:
                self.fail('incorrect_keys', ing_keys=ingredient.keys())

            ing_id = ingredient['id']

            if not Ingredient.objects.filter(id=ing_id).exists():
                self.fail('ing_not_exist', ing_id=ing_id)

            if int(ingredient['amount']) < 1:
                self.fail('amount_less_than_1', ing_id=ing_id)

            if ing_id in used_ingredients:
                self.fail('ing_repeat', ing_id=ing_id)

            used_ingredients.add(ing_id)

        return ingredients


class TagsField(serializers.Field):
    default_error_messages = {
        'empty_list': 'Не выбрано ни одного тега.',
        'incorrect_type': (
            'Неверный тип тега, ожидается: int, получен: {tag_id_type}.'
        ),
        'tag_not_exist': 'Тег с id {tag_id} не существует.',
        'tag_repeat': 'Тег {tag_id} передан больше 1 раза.',
    }

    def to_representation(self, tags):
        return tags.values()

    def to_internal_value(self, tags):
        if not tags:
            self.fail('empty_list')

        used_tags = set()
        for tag_id in tags:
            if not isinstance(tag_id, int):
                self.fail('incorrect_type', tag_id_type=type(tag_id))

            if not Tag.objects.filter(id=tag_id).exists():
                self.fail('tag_not_exist', tag_id=tag_id)

            if tag_id in used_tags:
                self.fail('tag_repeat', tag_id=tag_id)

            used_tags.add(tag_id)

        return tags


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    password = serializers.CharField(
        required=True,
        max_length=settings.PASSWORD_MAX_LEN,
        validators=[validate_pwd],
        write_only=True,
    )

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'password',
            'first_name',
            'last_name',
            'is_subscribed',
        ]
        read_only_fields = ['id', 'is_subscribed']

    def get_is_subscribed(self, user):
        request = self.context.get('request')
        if not request.user.is_anonymous:
            return request.user.following.filter(id=user.id).exists()
        return False

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )

    def to_representation(self, user):
        data = super().to_representation(user)
        if self.context.get('request').method == 'POST':
            data.pop('is_subscribed', None)
        return data


class ChangePasswordSerializer(serializers.Serializer):
    model = User

    current_password = serializers.CharField(
        required=True,
        max_length=settings.PASSWORD_MAX_LEN,
        validators=[validate_pwd],
    )
    new_password = serializers.CharField(
        required=True,
        max_length=settings.PASSWORD_MAX_LEN,
        validators=[validate_pwd],
    )

    def validate(self, data):
        if not self.context.get('request').user.check_password(
            data.get('current_password')
        ):
            raise serializers.ValidationError(
                {'current_password': ['Неверный пароль.']},
            )
        return data


class SubscriptionSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + ['recipes', 'recipes_count']
        read_only_fields = ['id']
        extra_kwargs = {'password': {'write_only': True}}

    def get_recipes(self, user):
        limit = self.context.get('request').GET.get('recipes_limit')
        recipes = (
            user.recipes.all()[: int(limit)] if limit else user.recipes.all()
        )
        serializer = ShortRecipeSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def get_recipes_count(self, user):
        return user.recipes.count()

    def to_representation(self, user):
        return super(UserSerializer, self).to_representation(user)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class ShortRecipeSerializer(serializers.ModelSerializer):
    image = CustomBase64ImageField()

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']
        read_only_fields = ['__all__']


class RecipeSerializer(ShortRecipeSerializer):
    ingredients = IngredientsField()
    tags = TagsField()
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        exclude = ['favorites', 'shopping_cart', 'created_at']

    def get_is_favorited(self, recipe):
        request = self.context.get('request')

        if not request.user.is_anonymous:
            if request.user in recipe.favorites.all():
                return True
        return False

    def get_is_in_shopping_cart(self, recipe):
        request = self.context.get('request')

        if not request.user.is_anonymous:
            if request.user in recipe.shopping_cart.all():
                return True
        return False

    @atomic
    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe(author=request.user, **validated_data)
        recipe.save()
        recipe.tags.set(tags)
        for ing in ingredients:
            IngredientQuantity.objects.create(
                recipe=recipe,
                ingredient=Ingredient.objects.filter(id=ing['id']).first(),
                amount=ing['amount'],
            )
        request.user.favorites.add(recipe.id)
        return recipe

    @atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        instance = super().update(
            instance=instance, validated_data=validated_data
        )
        instance.ingredients.clear()
        for ing in ingredients:
            IngredientQuantity.objects.create(
                recipe=instance,
                ingredient=Ingredient.objects.filter(id=ing['id']).first(),
                amount=ing['amount'],
            )
        return instance
