from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags']

    def filter_is_favorited(self, queryset, _, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(favorites__id=user.id)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, _, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(shopping_cart__id=user.id)
        return queryset
