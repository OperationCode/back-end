from django.contrib import admin

from .models import OldUserObj, UserInfo

admin.site.register([UserInfo, OldUserObj])
