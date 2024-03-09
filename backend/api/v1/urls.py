from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.views import IngredientViewSet, TagViewSet


router = DefaultRouter()
router.register('ingredients', IngredientViewSet, basename='ingredient')
router.register('tags', TagViewSet, basename='tag')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('users.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
