from django.contrib.auth import get_user_model
from django.db.models import F
from django.db.transaction import atomic
from rest_framework import serializers

from api.v1.mixins import CustomBase64ImageField
from api.v1.utils import ingredientquantity_bulk_create
from recipes.models import (
    FavoriteRecipes,
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag,
)
from users.models import FollowRelationship

User = get_user_model()


class IngredientsField(serializers.Field):
    """Custom field for ingredients."""

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
    """Custom field for tags."""

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
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscribed(self, user):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and request.user.following.filter(id=user.id).exists()
        )


class SubscriptionSerializer(UserSerializer):
    """Serializer for subscriptions endpoints."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + ['recipes', 'recipes_count']
        read_only_fields = ['id']
        extra_kwargs = {'password': {'write_only': True}}

    def get_recipes(self, user):
        limit = self.context.get('request').GET.get('recipes_limit')
        try:
            recipes = user.recipes.all()[: int(limit)]
        except (TypeError, ValueError):
            recipes = user.recipes.all()

        serializer = ShortRecipeSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def get_recipes_count(self, user):
        return user.recipes.count()

    def to_representation(self, user):
        return super(UserSerializer, self).to_representation(user)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Serializer for providing recipe shortcut in some endpoints."""

    image = CustomBase64ImageField()

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']
        read_only_fields = ['__all__']


class ReadRecipeSerializer(ShortRecipeSerializer):
    """Serializer for providing full recipe data."""

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
        return (
            request
            and request.user.is_authenticated
            and request.user in recipe.favorites.all()
        )

    def get_is_in_shopping_cart(self, recipe):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and request.user in recipe.shopping_cart.all()
        )


class WriteRecipeSerializer(ReadRecipeSerializer):
    """Serializer for saving and updating recipes."""

    @atomic
    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe(author=request.user, **validated_data)
        recipe.save()
        recipe.tags.set(tags)
        ingredientquantity_bulk_create(recipe, ingredients)
        request.user.favorites.add(recipe.id)
        return recipe

    @atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        instance = super().update(
            instance=instance, validated_data=validated_data
        )
        instance.ingredients.clear()
        ingredientquantity_bulk_create(instance, ingredients)
        return instance


class SaveFavoriteSerializer(serializers.ModelSerializer):
    """Serializer for saving user's favorite recipes."""

    class Meta:
        model = FavoriteRecipes
        fields = ['user', 'recipe']

    def to_representation(self, instance):
        return ShortRecipeSerializer(instance.recipe).data


class SaveShoppingCartSerializer(SaveFavoriteSerializer):
    """Serializer for adding recipes to user's shopping cart."""

    class Meta:
        model = ShoppingCart
        fields = ['user', 'recipe']


class SaveSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for saving users subscriptions."""

    class Meta:
        model = FollowRelationship
        exclude = ['created_at']

    def validate(self, data):
        if data['from_user'] == data['to_user']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя!'
            )
        return data

    def to_representation(self, instance):
        return SubscriptionSerializer(
            instance.to_user, context={'request': self.context.get('request')}
        ).data
