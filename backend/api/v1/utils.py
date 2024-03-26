from rest_framework import status
from rest_framework.response import Response

from recipes.models import IngredientQuantity


def add_obj(serializer):
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(
        serializer.data,
        status=status.HTTP_201_CREATED,
    )


def remove_obj(field, obj_id, obj_name='Объект'):
    if not field.filter(id=obj_id).exists():
        return Response(
            {'errors': f'{obj_name} с таким ID не найден!'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    field.remove(obj_id)
    return Response(status=status.HTTP_204_NO_CONTENT)


def ingredientquantity_bulk_create(recipe, ingredients):
    IngredientQuantity.objects.bulk_create(
        [
            IngredientQuantity(
                recipe=recipe,
                ingredient_id=ing['id'],
                amount=ing['amount'],
            )
            for ing in ingredients
        ]
    )
