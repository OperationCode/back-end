from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Profile

admin.site.unregister(User)


@admin.register(User)
class ExtendedUserAdmin(UserAdmin):
    list_display = ("email", "first_name", "last_name", "is_staff", "is_superuser")

    @staticmethod
    def suit_row_attributes(obj, request):  # pragma: no cover
        """
        Adds highlight to superusers in Users table
        """
        if obj.is_superuser:
            return {"class": "success"}


@admin.register(Profile)
class CodeSchoolAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "zipcode",
        "is_mentor",
        "verified",
        "state",
        "is_volunteer",
        "military_status",
    )

    list_filter = ("is_mentor", "state", "is_volunteer", "military_status")
    search_fields = ("user__email",)
