from django.contrib.auth import authenticate
from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view

from users.serializers import MyTokenObtainSerializer
from djoser.urls import authtoken


@api_view(['POST'])
def token_obtain(request):
    serializer = MyTokenObtainSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(User, email=serializer.data.get('email'))
