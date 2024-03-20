from django.contrib.auth import get_user_model
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1.serializers import (
    ChangePasswordSerializer,
    SubscriptionSerializer,
    UserSerializer,
)

User = get_user_model()


class UserModelViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(
        detail=False,
        methods=['get'],
        url_path='me',
        url_name='me',
        permission_classes=[permissions.IsAuthenticated],
    )
    def get_myself_user(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['post'],
        url_path='set_password',
        url_name='set_password',
        permission_classes=[permissions.IsAuthenticated],
    )
    def change_password(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.data.get('new_password'))
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

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
        methods=['post', 'delete'],
        url_path=r'(?P<user_id>\w+)/subscribe',
        url_name='subscribe',
        permission_classes=[permissions.IsAuthenticated],
    )
    def sub_unsub_user(self, request, user_id):
        user = request.user
        follow_user = User.objects.filter(id=user_id).first()

        if not follow_user:
            return Response(
                {'errors': f'Пользователь с id {user_id} не существует.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.method == 'POST':
            serializer = SubscriptionSerializer(
                follow_user,
                context={'request': request},
            )
            if user.following.filter(id=user_id).exists() or user.id == int(
                user_id
            ):
                return Response(
                    {
                        'errors': (
                            'Вы уже подписаны на данного пользователя, либо'
                            ' пытаетесь подписаться на самого себя!'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            request.user.following.add(user_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if user.following.filter(id=user_id).exists():
            request.user.following.remove(user_id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Вы не подписаны на данного пользователя!'},
            status=status.HTTP_400_BAD_REQUEST,
        )
