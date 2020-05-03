from django.contrib.auth.models import User
from django.db import models


class CodeSchool(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True)
    url = models.CharField(max_length=256, blank=True, null=True)
    logo = models.CharField(max_length=256, blank=True, null=True)
    full_time = models.BooleanField(blank=True, null=True)
    hardware_included = models.BooleanField(blank=True, null=True)
    has_online = models.BooleanField(blank=True, null=True)
    has_housing = models.BooleanField(default=False, null=True)
    online_only = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)
    mooc = models.BooleanField()
    is_partner = models.BooleanField()
    rep_name = models.CharField(max_length=256, blank=True, null=True)
    rep_email = models.CharField(max_length=256, blank=True, null=True)
    is_vet_tec_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.url}"

    class Meta:
        db_table = "api_code_schools"


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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"{self.code_school} - {self.address1} {self.city} {self.state} {self.zip}"
        )

    class Meta:
        db_table = "api_locations"


class Scholarship(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=256, blank=True, null=True)
    terms = models.TextField(blank=True, null=True)
    open_time = models.DateTimeField(blank=True, null=True)
    close_time = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.location}"


class ScholarshipApplication(models.Model):
    reason = models.TextField(blank=True, null=True)
    terms_accepted = models.BooleanField(blank=True, null=True)
    user = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True)
    scholarship = models.ForeignKey(
        Scholarship, models.DO_NOTHING, blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.scholarship}"


class TeamMember(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True)
    role = models.CharField(max_length=256, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True, null=True)
    group = models.CharField(max_length=256, blank=True, null=True)
    image_src = models.CharField(max_length=256, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.role}"

    class Meta:
        db_table = "api_team_members"


class SuccessStory(models.Model):
    created_by = models.CharField(max_length=256, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    text = models.TextField(blank=True, null=True)
    is_approved = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return f"{self.created_by} - {self.is_approved}"

    class Meta:
        verbose_name_plural = "Success Stories"
