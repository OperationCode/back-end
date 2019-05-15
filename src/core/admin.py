from django.contrib import admin

from .models import OldUserObj, Profile

admin.site.register([Profile, OldUserObj])
