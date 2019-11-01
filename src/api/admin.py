from django.contrib import admin

from api.models import (
    CodeSchool,
    Location,
    Scholarship,
    ScholarshipApplication,
    TeamMember,
)


@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "location",
        "open_time",
        "close_time",
        "created_at",
        "updated_at",
    )


@admin.register(ScholarshipApplication)
class ScholarshipApplicationAdmin(admin.ModelAdmin):
    list_display = ("user", "scholarship", "terms_accepted", "created_at", "updated_at")


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "role", "group", "image_src")


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        "code_school",
        "va_accepted",
        "address1",
        "address2",
        "city",
        "state",
        "zip",
    )


@admin.register(CodeSchool)
class CodeSchoolAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "url",
        "full_time",
        "hardware_included",
        "has_online",
        "online_only",
        "has_housing",
        "mooc",
        "is_partner",
        "is_vet_tec_approved",
        "rep_name",
        "rep_email",
    )

    list_filter = (
        "full_time",
        "hardware_included",
        "has_online",
        "online_only",
        "has_housing",
        "mooc",
        "is_partner",
        "is_vet_tec_approved",
    )

    search_fields = ("name", "rep_name", "rep_email", "url")
