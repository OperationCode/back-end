from django.db import models

from core.models import OldUserObj


class ActiveAdminComment(models.Model):
    namespace = models.CharField(max_length=256, blank=True, null=True)
    body = models.TextField(blank=True, null=True)
    resource_type = models.CharField(max_length=256, blank=True, null=True)
    resource_id = models.IntegerField(blank=True, null=True)
    author_type = models.CharField(max_length=256, blank=True, null=True)
    author_id = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "active_admin_comments"


class AdminUser(models.Model):
    email = models.CharField(unique=True, max_length=256)
    encrypted_password = models.CharField(max_length=256)
    reset_password_token = models.CharField(
        unique=True, max_length=256, blank=True, null=True
    )
    reset_password_sent_at = models.DateTimeField(blank=True, null=True)
    remember_created_at = models.DateTimeField(blank=True, null=True)
    sign_in_count = models.IntegerField()
    current_sign_in_at = models.DateTimeField(blank=True, null=True)
    last_sign_in_at = models.DateTimeField(blank=True, null=True)
    current_sign_in_ip = models.GenericIPAddressField(blank=True, null=True)
    last_sign_in_ip = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    role_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "admin_users"


class ArInternalMetadata(models.Model):
    key = models.CharField(primary_key=True, max_length=256)
    value = models.CharField(max_length=256, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "ar_internal_metadata"


class OldCodeSchool(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True)
    url = models.CharField(max_length=256, blank=True, null=True)
    logo = models.CharField(max_length=256, blank=True, null=True)
    full_time = models.BooleanField(blank=True, null=True)
    hardware_included = models.BooleanField(blank=True, null=True)
    has_online = models.BooleanField(blank=True, null=True)
    online_only = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    notes = models.TextField(blank=True, null=True)
    mooc = models.BooleanField()
    is_partner = models.BooleanField()
    rep_name = models.CharField(max_length=256, blank=True, null=True)
    rep_email = models.CharField(max_length=256, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.url}"

    class Meta:
        managed = False
        db_table = "code_schools"


class CodeSchool(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True)
    url = models.CharField(max_length=256, blank=True, null=True)
    logo = models.CharField(max_length=256, blank=True, null=True)
    full_time = models.BooleanField(blank=True, null=True)
    hardware_included = models.BooleanField(blank=True, null=True)
    has_online = models.BooleanField(blank=True, null=True)
    online_only = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    notes = models.TextField(blank=True, null=True)
    mooc = models.BooleanField()
    is_partner = models.BooleanField()
    rep_name = models.CharField(max_length=256, blank=True, null=True)
    rep_email = models.CharField(max_length=256, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.url}"

    class Meta:
        db_table = "api_code_schools"


class Event(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    url = models.CharField(max_length=256, blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    address1 = models.CharField(max_length=256, blank=True, null=True)
    address2 = models.CharField(max_length=256, blank=True, null=True)
    city = models.CharField(max_length=256, blank=True, null=True)
    state = models.CharField(max_length=256, blank=True, null=True)
    zip = models.CharField(max_length=256, blank=True, null=True)
    scholarship_available = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    source_id = models.CharField(max_length=256, blank=True, null=True)
    source_type = models.CharField(max_length=256, blank=True, null=True)
    source_updated = models.DateTimeField(blank=True, null=True)
    group = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "events"


class GitHubStatistic(models.Model):
    git_hub_user = models.ForeignKey(
        "GitHubUser", models.DO_NOTHING, blank=True, null=True
    )
    source_id = models.CharField(max_length=256, blank=True, null=True)
    source_type = models.CharField(max_length=256, blank=True, null=True)
    state = models.CharField(max_length=256, blank=True, null=True)
    additions = models.IntegerField(blank=True, null=True)
    deletions = models.IntegerField(blank=True, null=True)
    repository = models.CharField(max_length=256, blank=True, null=True)
    url = models.CharField(max_length=256, blank=True, null=True)
    title = models.CharField(max_length=256, blank=True, null=True)
    number = models.CharField(max_length=256, blank=True, null=True)
    completed_on = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "git_hub_statistics"


class GitHubUser(models.Model):
    user_id = models.IntegerField(blank=True, null=True)
    git_hub_login = models.CharField(max_length=256, blank=True, null=True)
    avatar_url = models.CharField(max_length=256, blank=True, null=True)
    api_url = models.CharField(max_length=256, blank=True, null=True)
    html_url = models.CharField(max_length=256, blank=True, null=True)
    git_hub_id = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "git_hub_users"


class OldLocation(models.Model):
    va_accepted = models.BooleanField(blank=True, null=True)
    address1 = models.CharField(max_length=256, blank=True, null=True)
    address2 = models.CharField(max_length=256, blank=True, null=True)
    city = models.CharField(max_length=256, blank=True, null=True)
    state = models.CharField(max_length=256, blank=True, null=True)
    zip = models.IntegerField(blank=True, null=True)
    code_school = models.ForeignKey(
        OldCodeSchool,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="locations",
    )
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    def __str__(self):
        return (
            f"{self.code_school} - {self.address1} {self.city} {self.state} {self.zip}"
        )

    class Meta:
        managed = False
        db_table = "locations"


class Location(models.Model):
    va_accepted = models.BooleanField(blank=True, null=True)
    address1 = models.CharField(max_length=256, blank=True, null=True)
    address2 = models.CharField(max_length=256, blank=True, null=True)
    city = models.CharField(max_length=256, blank=True, null=True)
    state = models.CharField(max_length=256, blank=True, null=True)
    zip = models.IntegerField(blank=True, null=True)
    code_school = models.ForeignKey(
        CodeSchool, models.DO_NOTHING, blank=True, null=True, related_name="locations"
    )
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    def __str__(self):
        return (
            f"{self.code_school} - {self.address1} {self.city} {self.state} {self.zip}"
        )

    class Meta:
        db_table = "api_locations"


class Request(models.Model):
    service_id = models.IntegerField(blank=True, null=True)
    language = models.CharField(max_length=256, blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    user = models.ForeignKey(OldUserObj, models.DO_NOTHING, blank=True, null=True)
    assigned_mentor_id = models.IntegerField(blank=True, null=True)
    requested_mentor_id = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    status = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "requests"


class Resource(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True)
    url = models.CharField(max_length=256, blank=True, null=True)
    category = models.CharField(max_length=256, blank=True, null=True)
    language = models.CharField(max_length=256, blank=True, null=True)
    paid = models.BooleanField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    votes_count = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "resources"


class Role(models.Model):
    title = models.CharField(max_length=256, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    def __str__(self):
        return f"{self.title}"

    class Meta:
        managed = False
        db_table = "roles"


class SchemaMigration(models.Model):
    version = models.CharField(primary_key=True, max_length=256)

    class Meta:
        managed = False
        db_table = "schema_migrations"


class ScholarshipApplication(models.Model):
    reason = models.TextField(blank=True, null=True)
    terms_accepted = models.BooleanField(blank=True, null=True)
    user = models.ForeignKey(OldUserObj, models.DO_NOTHING, blank=True, null=True)
    scholarship = models.ForeignKey(
        "Scholarship", models.DO_NOTHING, blank=True, null=True
    )
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "scholarship_applications"


class Scholarship(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=256, blank=True, null=True)
    terms = models.TextField(blank=True, null=True)
    open_time = models.DateTimeField(blank=True, null=True)
    close_time = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "scholarships"


class Service(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "services"


class SlackUser(models.Model):
    slack_id = models.CharField(max_length=256, blank=True, null=True)
    slack_name = models.CharField(max_length=256, blank=True, null=True)
    slack_real_name = models.CharField(max_length=256, blank=True, null=True)
    slack_display_name = models.CharField(max_length=256, blank=True, null=True)
    slack_email = models.CharField(max_length=256, blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "slack_users"


class Tagging(models.Model):
    tag_id = models.IntegerField(blank=True, null=True)
    taggable_type = models.CharField(max_length=256, blank=True, null=True)
    taggable_id = models.IntegerField(blank=True, null=True)
    tagger_type = models.CharField(max_length=256, blank=True, null=True)
    tagger_id = models.IntegerField(blank=True, null=True)
    context = models.CharField(max_length=128, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.tag_id}"

    class Meta:
        managed = False
        db_table = "taggings"
        unique_together = (
            (
                "tag_id",
                "taggable_id",
                "taggable_type",
                "context",
                "tagger_id",
                "tagger_type",
            ),
        )


class Tag(models.Model):
    name = models.CharField(unique=True, max_length=256, blank=True, null=True)
    taggings_count = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.taggings_count}"

    class Meta:
        managed = False
        db_table = "tags"


class OldTeamMember(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True)
    role = models.CharField(max_length=256, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    description = models.TextField(blank=True, null=True)
    group = models.CharField(max_length=256, blank=True, null=True)
    image_src = models.CharField(max_length=256, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.role}"

    class Meta:
        managed = False
        db_table = "team_members"


class TeamMember(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True)
    role = models.CharField(max_length=256, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    description = models.TextField(blank=True, null=True)
    group = models.CharField(max_length=256, blank=True, null=True)
    image_src = models.CharField(max_length=256, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.role}"

    class Meta:
        db_table = "api_team_members"


class Vote(models.Model):
    user = models.ForeignKey(OldUserObj, models.DO_NOTHING, blank=True, null=True)
    resource = models.ForeignKey(Resource, models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "votes"
