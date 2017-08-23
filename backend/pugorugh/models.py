from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save

GENDERS = (
    ('m', 'male'),
    ('f', 'female'),
    ('u', 'unknown')
)

SIZE = (
    ('s', 'small'),
    ('m', 'medium'),
    ('l', 'large'),
    ('xl', 'extra large'),
    ('u', 'unknown'),
)

STATUS = (
    ('l', 'liked'),
    ('d', 'dislike'),
)

AGE = (
    ('b', 'baby'),
    ('y', 'young'),
    ('a', 'adult'),
    ('s', 'senior'),
)


class Dog(models.Model):
    name = models.CharField(max_length=100)
    image_filename = models.CharField(max_length=30, default='')
    breed = models.CharField(max_length=255, default='Unknown breed')
    age = models.IntegerField(default=1, blank=True)
    gender = models.CharField(choices=GENDERS, default='Unknown', max_length=15)
    size = models.CharField(choices=SIZE, max_length=8, default='Unknown')

    def __str__(self):
        return self.name


class UserDog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dog = models.ForeignKey(Dog, on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS, max_length=10, default='Undecided')

    def __str__(self):
        return '{} {} {}'.format(self.user, self.dog, self.get_status_display())


class UserPref(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    age = models.CharField(choices=AGE, max_length=8, default='b,y,a,s')
    gender = models.CharField(max_length=30, choices=GENDERS, default='f, m')
    size = models.CharField(max_length=30, choices=SIZE, default='s, m, l, xl')

    def __str__(self):
        return '{} preferred dog'.format(self.user)


def create_userpref(sender, **kwargs):
    user = kwargs['instance']

    if kwargs['created']:
        UserPref.objects.create(user=user)

post_save.connect(create_userpref, sender=User)
