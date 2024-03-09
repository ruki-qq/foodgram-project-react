from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import UserModelViewSet


v1_router = DefaultRouter()

v1_router.register('users', UserModelViewSet, basename='user')

urlpatterns = [
    path('', include(v1_router.urls)),
]
