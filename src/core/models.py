from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """
    Model used to extend Django's base User model
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    zipcode = models.CharField(max_length=256, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    remember_created_at = models.DateTimeField(blank=True, null=True)
    sign_in_count = models.IntegerField(blank=True, null=True)
    is_mentor = models.BooleanField(blank=True, null=True, default=False)
    timezone = models.CharField(max_length=256, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    verified = models.BooleanField(default=False)
    state = models.CharField(max_length=256, blank=True, null=True)
    address_1 = models.CharField(max_length=256, blank=True, null=True)
    address_2 = models.CharField(max_length=256, blank=True, null=True)
    city = models.CharField(max_length=256, blank=True, null=True)
    is_volunteer = models.BooleanField(blank=True, null=True, default=False)
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
    wants_scholarship_info = models.BooleanField(blank=True, null=True)
    role_id = models.IntegerField(blank=True, null=True)
    military_status = models.CharField(max_length=256, blank=True, null=True)

    programming_languages = models.CharField(max_length=256, blank=True, null=True)
    disciplines = models.CharField(max_length=256, blank=True, null=True)

    slack_id = models.CharField(max_length=16, blank=True)

    def __str__(self):
        return f"Username: {self.user} Slack ID: {self.slack_id}"

    class Meta:
        db_table = "profile"


@receiver(post_save, sender=User)
def create_profile(instance: User, created: bool, **kwargs: dict) -> None:
    """
    Function creates an empty Profile attached to the created User upon creation
    """
    if created:
        try:
            instance.profile
        except Profile.DoesNotExist:
            Profile.objects.create(user=instance)


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
