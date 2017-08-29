from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from rest_framework.authtoken.models import Token

from . import models
from . import serializers

# Create your tests here.

DOG1 = {
    "name": "Larry",
    "image_filename": "1.jpg",
    "breed": "Labrador",
    "age": 72,
    "gender": "f",
    "size": "l"
  }

DOG2 = {
    "name": "Jon",
    "image_filename": "2.jpg",
    "breed": "French Bulldog",
    "age": 14,
    "gender": "m",
    "size": "s"
  }

DOG3 = {
    "name": "Bjorn",
    "image_filename": "4.jpg",
    "breed": "Swedish Vallhund",
    "age": 36,
    "gender": "m",
    "size": "m"
  }

USER_DATA = {
    'username': 'usertest',
    'password': 'password1',

}


##### Views Test #####
class TestSetUp(APITestCase):
    def setUp(self):

        self.client = APIClient()
        self.test_user = get_user_model().objects.create(**USER_DATA)
        self.test_dog1 = models.Dog.objects.create(**DOG1)
        self.test_dog2 = models.Dog.objects.create(**DOG2)
        self.test_dog3 = models.Dog.objects.create(**DOG3)
        self.client.login(username='usertest', password='password1')
        self.token = Token.objects.create(user=self.test_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def tearDown(self):
        self.test_user.delete()
        self.test_dog2.delete()
        self.test_dog1.delete()
        self.test_dog3.delete()
        self.client.logout()


class DogFilterViewsTestCase(TestSetUp):
    def test_dog_list(self):
        resp = self.client.get('/api/dog/1/')
        self.assertEqual(resp.status_code, 200)


class DogViewSetTestCase(TestSetUp):
    def test_liked_dog_put(self):
        resp = self.client.put('/api/dog/1/liked/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['status'], 'l')

    def test_liked_dog_post(self):
        resp = self.client.post('/api/dog/3/liked/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['status'], 'l')

    def test_disliked_dog_put(self):
        resp = self.client.put('/api/dog/3/disliked/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['status'], 'd')

    def test_diliked_dog_post(self):
        resp = self.client.post('/api/dog/1/disliked/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['status'], 'd')

    def test_undecided_dog_put(self):
        resp = self.client.put('/api/dog/2/undecided/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['status'], 'u')

    def test_undecided_dog_post(self):
        resp = self.client.post('/api/dog/1/liked/')
        self.assertTrue(resp.status_code, 200)
        self.assertTrue(resp.data['status'], 'u')

    def test_delete_dog(self):
        resp = self.client.delete('/api/dog/1/')
        self.assertEqual(resp.status_code, 204)

    def test_create_dog(self):
        resp = self.client.post('/api/dog/',
                                {
                                  "name": "Test",
                                  "image_filename": "11.jpg",
                                  "breed": "PitBull",
                                  "age": 15,
                                  "gender": "f",
                                  "size": "m"
                                }
                                )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data['name'], 'Test')

    def test_update_dog(self):
        resp = self.client.put('/api/dog/1/',
                               {'name': 'Tommy'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['name'], 'Tommy')


class UserPrefViewSetTestCase(TestSetUp):
    def test_userpref_get(self):
        resp = self.client.get('/api/user/preferences/')
        self.test_userpref = models.UserPref.objects.get(user=self.test_user)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['gender'], self.test_userpref.gender)

    def test_userpref_put(self):
        resp = self.client.put('/api/user/preferences/',
                               {'age': ['b', 'a'], 'gender': 'f', 'size': ['s', 'm']}
                               )
        self.test_userpref = models.UserPref.objects.get(user=self.test_user)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['age'], self.test_userpref.age)


##### Serializer Test #####
class DogSerializerTest(TestCase):
    def setUp(self):
        self.test_dog = models.Dog.objects.create(**DOG1)
        self.serializer = serializers.DogSerializer(self.test_dog)

    def tearDown(self):
        self.test_dog.delete()

    def test_dog_serializer(self):
        data = self.serializer.data
        self.assertCountEqual(data.keys(), ['id', 'name', 'image_filename', 'breed', 'age', 'gender', 'size', 'sterilized'])
        self.assertEqual(data['name'], DOG1['name'])
        self.assertEqual(data['gender'], 'f')


class UserDogSerilizerTest(TestCase):
    def setUp(self):
        self.test_user = models.User.objects.create(**USER_DATA)
        self.test_dog = models.Dog.objects.create(**DOG1)
        self.user_dog = models.UserDog.objects.create(
            user=self.test_user,
            dog=self.test_dog,
            status='d'
        )
        self.serializer = serializers.UserDogSerializer(self.user_dog)

    def tearDown(self):
        self.test_dog.delete()
        self.test_user.delete()
        self.user_dog.delete()

    def test_userdog_serializer(self):
        data = self.serializer.data
        self.assertEqual(data['status'], 'd')
        self.assertCountEqual(data.keys(), ['status', 'dog'])


class UserPrefSerializerTest(TestCase):
    def setUp(self):
        self.test_user = models.User.objects.create(**USER_DATA)
        self.user_pref = models.UserPref.objects.create(
            user=self.test_user,
            age='a',
            gender='m'
        )
        self.serialize = serializers.UserPrefSerializer(self.user_pref)

    def tearDown(self):
        self.test_user.delete()
        self.user_pref.delete()

    def test_userpref_serializer(self):
        data = self.serialize.data
        self.assertEqual(data['age'], 'a')
        self.assertEqual(data['gender'], 'm')
        self.assertCountEqual(data.keys(), ['age', 'gender', 'size', 'sterilized'])


#### Model Tests #####
class DogModelTestCase(TestCase):
    def test_create_dog(self):
        dog = models.Dog.objects.create(**DOG1)
        self.assertEqual(dog.name, 'Larry')
        self.assertEqual(dog.size, 'l')


class DogUserModelTestCase(TestCase):
    def setUp(self):
        self.test_user = get_user_model().objects.create(**USER_DATA)
        self.test_dog = models.Dog.objects.create(**DOG2)

    def tearDown(self):
        self.test_user.delete()
        self.test_dog.delete()

    def test_user_dog(self):
        user_dog = models.UserDog.objects.create(
            user=self.test_user,
            dog=self.test_dog,
            status='l'
        )
        self.assertEqual('usertest', user_dog.user.username)
        self.assertEqual('l', user_dog.status)
        self.assertEqual('French Bulldog', user_dog.dog.breed)


class UserPrefModelTestCase(TestCase):
    def setUp(self):
        self.test_user = get_user_model().objects.create(**USER_DATA)

    def tearDown(self):
        self.test_user.delete()

    def test_user_pref(self):
        user_pref = models.UserPref.objects.get(user=self.test_user)
        self.assertEqual(user_pref.user.username, 'usertest')
        self.assertIn('m', user_pref.gender)
        self.assertIn('l', user_pref.size)
        self.assertIn('a', user_pref.age)
