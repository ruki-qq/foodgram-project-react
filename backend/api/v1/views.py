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
    RecipeSerializer,
    TagSerializer,
)
from core.utils import add_rm_recipe
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
    serializer_class = RecipeSerializer
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def update(self, request, *args, **kwargs):
        return super().update(request, partial=False)

    @action(
        detail=False,
        methods=['post', 'delete'],
        url_path=r'(?P<recipe_id>\w+)/favorite',
        url_name='favorite',
        permission_classes=[permissions.IsAuthenticated],
    )
    def add_rm_favorite_recipe(self, request, recipe_id):
        return add_rm_recipe(
            request.user.favorites,
            recipe_id,
            request.method,
            'Избранный рецепт',
        )

    @action(
        detail=False,
        methods=['post', 'delete'],
        url_path=r'(?P<recipe_id>\w+)/shopping_cart',
        url_name='shopping_cart',
        permission_classes=[permissions.IsAuthenticated],
    )
    def add_rm_shopping_cart(self, request, recipe_id):
        return add_rm_recipe(
            request.user.shopping_cart,
            recipe_id,
            request.method,
            'Рецепт в корзине покупок',
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
