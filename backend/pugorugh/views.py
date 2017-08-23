from django.contrib.auth import get_user_model

from rest_framework import permissions, generics

from . import serializers
from . import models


AGES = {
    'b': list(range(0, 12)),
    'y': list(range(12, 36)),
    'a': list(range(36, 108)),
    's': list(range(108, 200)),
}


def get_age(keys='b,y,a,s'):
    """Gets the ages of the dogs in a range based on their age in months"""
    data = []
    for key in keys.split(','):
        data.extend(AGES['key'])
    return data


class DogFilterView(generics.RetrieveAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = models.Dog.objects.all()
    serializer_class = serializers.DogSerializer


class UserRegisterView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    model = get_user_model()
    serializer_class = serializers.UserSerializer