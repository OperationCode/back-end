from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from date_range_filter import DateRangeFilter

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
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "zipcode",
        "is_mentor",
        "verified",
        "state",
        "is_volunteer",
        "military_status",
        "branch_of_service",
        "created_at",
    )

    list_filter = (
        "is_mentor",
        "state",
        "is_volunteer",
        "military_status",
        "branch_of_service",
        ("created_at", DateRangeFilter),
    )
    search_fields = ("user__email",)
