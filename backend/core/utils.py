from rest_framework import status
from rest_framework.response import Response

from api.v1.serializers import ShortRecipeSerializer
from recipes.models import Recipe


def _add_obj(field, obj_id, serializer, obj_name='Объект'):
    if not field.filter(id=obj_id).exists():
        field.add(obj_id)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )
    return Response(
        {'errors': f'{obj_name} с таким ID уже существует!'},
        status=status.HTTP_400_BAD_REQUEST,
    )


def _remove_obj(field, obj_id, obj_name='Объект'):
    if field.filter(id=obj_id).exists():
        field.remove(obj_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(
        {'errors': f'{obj_name} с таким ID не найден!'},
        status=status.HTTP_400_BAD_REQUEST,
    )


def add_rm_recipe(field, recipe_id, method, name='Рецепт'):
    favorite_recipe = Recipe.objects.filter(id=recipe_id).first()
    if not favorite_recipe:
        return Response(
            {'errors': f'Рецепт с id {recipe_id} не существует.'},
            status=status.HTTP_404_NOT_FOUND,
        )
    if method == 'POST':
        serializer = ShortRecipeSerializer(favorite_recipe)
        return _add_obj(
            field,
            recipe_id,
            serializer,
            name,
        )
    return _remove_obj(field, recipe_id, name)
