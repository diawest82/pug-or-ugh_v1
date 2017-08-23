from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Dog)
admin.site.register(UserPref)
admin.site.register(UserDog)
