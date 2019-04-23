from django.contrib import admin

from .models import User, UserInfo

admin.site.register([UserInfo, User])
