from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions
from rest_framework.decorators import action

from api.v1.serializers import (
    SaveSubscriptionSerializer,
    SubscriptionSerializer,
    UserSerializer,
)
from core.utils import add_obj, remove_obj

User = get_user_model()


class UserModelViewSet(UserViewSet):
    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    @action(
        detail=False,
        methods=['get'],
        url_path='subscriptions',
        url_name='subscriptions',
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscriptions_user(self, request):
        queryset = request.user.following.all()
        serializer = SubscriptionSerializer(
            self.paginate_queryset(queryset),
            many=True,
            context={'request': request},
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=['post'],
        url_path=r'(?P<user_id>\w+)/subscribe',
        url_name='subscribe',
        permission_classes=[permissions.IsAuthenticated],
    )
    def sub_user(self, request, user_id):
        get_object_or_404(User, id=user_id)
        return add_obj(
            SaveSubscriptionSerializer(
                data={'from_user': request.user.id, 'to_user': user_id},
                context={'request': request},
            )
        )

    @sub_user.mapping.delete
    def unsub_user(self, request, user_id):
        get_object_or_404(User, id=user_id)
        return remove_obj(
            request.user.following, user_id, 'Пользователь в подписках'
        )
