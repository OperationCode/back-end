from django.contrib.auth.models import User as AuthUser
from django.db import models

from django.db.models.signals import post_save
from django.dispatch import receiver


class UserInfo(models.Model):
    """
    Model used to extend Django's base User model
    """

    user = models.OneToOneField(AuthUser, on_delete=models.CASCADE)

    zip = models.CharField(max_length=256, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    remember_created_at = models.DateTimeField(blank=True, null=True)
    sign_in_count = models.IntegerField(blank=True, null=True)
    mentor = models.BooleanField(blank=True, null=True, default=False)
    timezone = models.CharField(max_length=256, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    verified = models.BooleanField(default=False)
    state = models.CharField(max_length=256, blank=True, null=True)
    address_1 = models.CharField(max_length=256, blank=True, null=True)
    address_2 = models.CharField(max_length=256, blank=True, null=True)
    city = models.CharField(max_length=256, blank=True, null=True)
    volunteer = models.BooleanField(blank=True, null=True, default=False)
    branch_of_service = models.CharField(max_length=256, blank=True, null=True)
    years_of_service = models.FloatField(blank=True, null=True)
    pay_grade = models.CharField(max_length=256, blank=True, null=True)
    military_occupational_specialty = models.CharField(
        max_length=256, blank=True, null=True
    )
    github = models.CharField(max_length=256, blank=True, null=True)
    twitter = models.CharField(max_length=256, blank=True, null=True)
    linkedin = models.CharField(max_length=256, blank=True, null=True)
    employment_status = models.CharField(max_length=256, blank=True, null=True)
    education = models.CharField(max_length=256, blank=True, null=True)
    company_role = models.CharField(max_length=256, blank=True, null=True)
    company_name = models.CharField(max_length=256, blank=True, null=True)
    education_level = models.CharField(max_length=256, blank=True, null=True)
    interests = models.CharField(max_length=256, blank=True, null=True)
    scholarship_info = models.BooleanField(blank=True, null=True)
    role_id = models.IntegerField(blank=True, null=True)
    military_status = models.CharField(max_length=256, blank=True, null=True)

    slack_id = models.CharField(max_length=16)

    def __str__(self):
        return f"Username: {self.user} Slack ID: {self.slack_id}"

    class Meta:
        db_table = "userinfo"


@receiver(post_save, sender=AuthUser)
def create_user_info(sender, instance, created, **kwargs):
    """
    Function creates an empty UserInfo attached to the created AuthUser upon creation
    """
    if created:
        try:
            instance.userinfo
        except UserInfo.DoesNotExist:
            UserInfo.objects.create(user=instance)


class OldUserObj(models.Model):
    email = models.CharField(unique=True, max_length=256, blank=True, null=True)
    zip = models.CharField(max_length=256, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
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
    mentor = models.BooleanField(blank=True, null=True)
    first_name = models.CharField(max_length=256, blank=True, null=True)
    last_name = models.CharField(max_length=256, blank=True, null=True)
    timezone = models.CharField(max_length=256, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    verified = models.BooleanField()
    state = models.CharField(max_length=256, blank=True, null=True)
    address_1 = models.CharField(max_length=256, blank=True, null=True)
    address_2 = models.CharField(max_length=256, blank=True, null=True)
    city = models.CharField(max_length=256, blank=True, null=True)
    username = models.CharField(max_length=256, blank=True, null=True)
    volunteer = models.BooleanField(blank=True, null=True)
    branch_of_service = models.CharField(max_length=256, blank=True, null=True)
    years_of_service = models.FloatField(blank=True, null=True)
    pay_grade = models.CharField(max_length=256, blank=True, null=True)
    military_occupational_specialty = models.CharField(
        max_length=256, blank=True, null=True
    )
    github = models.CharField(max_length=256, blank=True, null=True)
    twitter = models.CharField(max_length=256, blank=True, null=True)
    linkedin = models.CharField(max_length=256, blank=True, null=True)
    employment_status = models.CharField(max_length=256, blank=True, null=True)
    education = models.CharField(max_length=256, blank=True, null=True)
    company_role = models.CharField(max_length=256, blank=True, null=True)
    company_name = models.CharField(max_length=256, blank=True, null=True)
    education_level = models.CharField(max_length=256, blank=True, null=True)
    interests = models.CharField(max_length=256, blank=True, null=True)
    scholarship_info = models.BooleanField(blank=True, null=True)
    role_id = models.IntegerField(blank=True, null=True)
    military_status = models.CharField(max_length=256, blank=True, null=True)

    def __str__(self):
        return f"{self.email} - {self.first_name} {self.last_name}"

    class Meta:
        managed = False
        db_table = "users"
