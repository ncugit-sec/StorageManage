from django.shortcuts import render
from django.contrib.auth import get_user_model
from jwt_server.serializers import RegisterSerializer
from rest_framework import generics
from rest_framework import permissions

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer
