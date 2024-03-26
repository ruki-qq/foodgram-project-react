from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1.filters import IngredientFilter, RecipeFilter
from api.v1.permissions import IsOwnerOrReadOnly
from api.v1.serializers import (
    IngredientSerializer,
    ReadRecipeSerializer,
    SaveFavoriteSerializer,
    SaveShoppingCartSerializer,
    TagSerializer,
    WriteRecipeSerializer,
)
from api.v1.utils import add_obj, remove_obj
from recipes.models import Ingredient, IngredientQuantity, Recipe, Tag


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None

    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return ReadRecipeSerializer
        return WriteRecipeSerializer

    def update(self, request, *args, **kwargs):
        return super().update(request, partial=False)

    @action(
        detail=False,
        methods=['post'],
        url_path=r'(?P<recipe_id>\w+)/favorite',
        url_name='favorite',
        permission_classes=[permissions.IsAuthenticated],
    )
    def add_favorite_recipe(self, request, recipe_id):
        return add_obj(
            SaveFavoriteSerializer(
                data={'user': request.user.id, 'recipe': recipe_id}
            )
        )

    @add_favorite_recipe.mapping.delete
    def rm_favorite_recipe(self, request, recipe_id):
        return remove_obj(
            request.user.favorites, recipe_id, 'Избранный рецепт'
        )

    @action(
        detail=False,
        methods=['post'],
        url_path=r'(?P<recipe_id>\w+)/shopping_cart',
        url_name='shopping_cart',
        permission_classes=[permissions.IsAuthenticated],
    )
    def add_shopping_cart(self, request, recipe_id):
        return add_obj(
            SaveShoppingCartSerializer(
                data={'user': request.user.id, 'recipe': recipe_id}
            )
        )

    @add_shopping_cart.mapping.delete
    def rm_shopping_cart(self, request, recipe_id):
        return remove_obj(
            request.user.shopping_cart, recipe_id, 'Рецепт в корзине покупок'
        )

    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
        permission_classes=[permissions.IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        user = request.user

        if not user.shopping_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        key_names = {
            'ingredient__name': 'Ингредиент',
            'ingredient__measurement_unit': 'Мера измерения',
            'amount': 'Количество',
        }

        ingredients = (
            IngredientQuantity.objects.filter(
                recipe__shopping_cart__id=user.id
            )
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(amount=Sum('amount'))
        )

        response = HttpResponse(content_type='text/plain')
        response[
            'Content-Disposition'
        ] = 'attachment; filename="shopping_cart.txt"'

        response.write('Список покупок:\n')

        for ing in ingredients:
            for key, val in ing.items():
                response.write(f'{key_names[key]}: {val}; ')
            response.write('\n')

        return response
