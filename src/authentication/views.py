from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from authentication.serializers import UserSerializer
from authentication.permissions import UserPermission
User = get_user_model()

# Create your views here.


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [UserPermission]
