from django.contrib import admin

from api.models import (
    CodeSchool,
    Location,
    Scholarship,
    ScholarshipApplication,
    TeamMember,
)

admin.site.register([Location, Scholarship, ScholarshipApplication, TeamMember])


@admin.register(CodeSchool)
class CodeSchoolAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "url",
        "full_time",
        "hardware_included",
        "has_online",
        "online_only",
        "mooc",
        "is_partner",
        "rep_name",
        "rep_email",
    )

    list_filter = (
        "full_time",
        "hardware_included",
        "has_online",
        "online_only",
        "mooc",
        "is_partner",
    )

    search_fields = ("name", "rep_name", "rep_email")
