from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import Http404

from rest_framework import permissions, generics, viewsets, mixins
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response

from . import serializers
from . import models

STATUS = ['liked', 'disliked']

AGES = {
    'b': list(range(0, 12)),
    'y': list(range(12, 36)),
    'a': list(range(36, 108)),
    's': list(range(108, 200)),
}


def get_age(keys='b,y,a,s'):
    """Gets the age range of a dog based on their age in months"""
    data = []
    for key in keys.split(','):
        data.extend(AGES[key])
    return data


class DogFilterView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.DogSerializer

    # returns the queryset of the specific search
    def get_ids(self, queryset):
        if queryset is not None:
            return [userdog.dog.pk for userdog in queryset]
        return []

    # Filters the dogs based on the user preferences
    def pref_filter(self, dog_filter, user_prefs):
        userdog_query = models.UserDog.objects.select_related('dog').filter(user=user_prefs.user.pk)
        ages = get_age(user_prefs.age)
        queryset = models.Dog.objects.filter(
            gender__in=user_prefs.gender.split(','),
            size__in=user_prefs.size.split(','),
            age__in=ages
        )
        # Search for undecided dogs
        if dog_filter not in STATUS:
            dogs = self.get_ids(userdog_query.exclude(status__startswith='u'))
            queryset = queryset.exclude(pk__in=dogs)
        # Search by dog filter in STATUS based on dogs user likes
        else:
            userdog_query = userdog_query.filter(status__in=dog_filter[0])
            dogs = self.get_ids(userdog_query)
            queryset = queryset.filter(pk__in=dogs)

        return queryset.order_by('pk')

    def get_queryset(self):
        user = self.request.user
        dog_filter = self.kwargs.get('dog_filter')
        user_prefs = get_object_or_404(models.UserPref, user=user)
        # Returns a query based on ages(months) and user preferences
        queryset = self.pref_filter(dog_filter, user_prefs)
        return queryset

    def get_object(self):
        pk = int(self.kwargs.get('pk'))
        # filter the query by the NEXT dog
        queryset = self.get_queryset().filter(
            pk__gt=pk
        )
        obj = queryset.first()
        if not obj:
            raise Http404
        return obj


class DogViewSet(mixins.CreateModelMixin,
                 mixins.RetrieveModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.DestroyModelMixin,
                 viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.DogSerializer
    queryset = models.Dog.objects.all()

    # View for dog/<pk>/liked
    @detail_route(methods=['POST', 'PUT'])
    def liked(self, request, pk=None):
        user = request.user
        dog = self.get_object()
        user_dog, created = models.UserDog.objects.get_or_create(
            user=user, dog=dog
        )
        user_dog.status = 'l'
        user_dog.save()
        serializer = serializers.UserDogSerializer(user_dog)
        return Response(serializer.data)

    # view for dog/<pk>/disliked
    @detail_route(methods=['POST', 'PUT'])
    def disliked(self, request, pk=None):
        user = request.user
        dog = self.get_object()
        user_dog, created = models.UserDog.objects.get_or_create(
            user=user, dog=dog
        )
        user_dog.status = 'd'
        user_dog.save()
        serializer = serializers.UserDogSerializer(user_dog)
        return Response(serializer.data)

    # view for dog/<pk>/undecided
    @detail_route(methods=['POST', 'PUT'])
    def undecided(self, request, pk=None):
        user = request.user
        dog = self.get_object()
        user_dog, created = models.UserDog.objects.get_or_create(
            user=user, dog=dog
        )
        user_dog.status = 'u'
        user_dog.save()
        serializer = serializers.UserDogSerializer(user_dog)
        return Response(serializer.data)


class UserPrefViewSet(mixins.UpdateModelMixin,
                      mixins.RetrieveModelMixin,
                      viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = models.UserPref.objects.all()
    serializer_class = serializers.UserPrefSerializer

    @list_route(methods=["GET", "put"])
    def preferences(self, request, pk=None):
        user = request.user
        user_pref = models.UserPref.objects.get(user=user)

        if request.method == 'PUT':
            data = request.data
            user_pref.age = data.get('age')
            user_pref.gender = data.get('gender')
            user_pref.size = data.get('size')
            user_pref.save()

        serializer = serializers.UserPrefSerializer(user_pref)
        return Response(serializer.data)


class UserRegisterView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    model = get_user_model()
    serializer_class = serializers.UserSerializer
