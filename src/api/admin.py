from django.contrib import admin

from api.models import (
    ActiveAdminComment,
    AdminUser,
    ArInternalMetadata,
    CodeSchool,
    Event,
    GitHubStatistic,
    GitHubUser,
    Location,
    Request,
    Resource,
    Role,
    SchemaMigration,
    Scholarship,
    ScholarshipApplication,
    Service,
    SlackUser,
    Tag,
    Tagging,
    TeamMember,
    Vote,
)

admin.site.register(
    [
        ActiveAdminComment,
        AdminUser,
        ArInternalMetadata,
        Event,
        GitHubStatistic,
        GitHubUser,
        Location,
        Request,
        Resource,
        Role,
        SchemaMigration,
        ScholarshipApplication,
        Scholarship,
        Service,
        SlackUser,
        Tagging,
        Tag,
        TeamMember,
        Vote,
    ]
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
