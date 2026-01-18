import logging

from allauth.account.models import EmailConfirmation
from allauth.account.signals import email_confirmed, user_signed_up
from dj_rest_auth.serializers import JWTSerializer
from django.contrib.auth.models import User
from django.dispatch import receiver
from django_q.tasks import async_task
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

logger = logging.getLogger(__name__)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom token serializer that adds extra claims to the JWT token.
    """

    @classmethod
    def get_token(cls, user: User):
        token = super().get_token(user)

        # Add custom claims
        token["email"] = user.email
        token["firstName"] = user.first_name
        token["lastName"] = user.last_name

        # Add profile data if available
        if hasattr(user, "profile"):
            token["zipcode"] = user.profile.zipcode
            token["isMentor"] = user.profile.is_mentor

        return token


class BackwardsCompatibleJWTSerializer(JWTSerializer):
    """
    Custom JWT serializer that adds 'token' as an alias for 'access'
    for backwards compatibility with PyBot and other clients.
    """

    token = serializers.SerializerMethodField()

    def get_token(self, obj):
        """Return the access token as 'token' for backwards compatibility."""
        return str(obj.get("access", ""))

    def to_representation(self, instance):
        """Add 'token' field to the response while keeping 'access' and 'refresh'."""
        data = super().to_representation(instance)
        # Add 'token' as alias for 'access' for backwards compatibility
        data["token"] = data.get("access", "")
        return data


@receiver(user_signed_up)
def registration_callback(user: User, **kwargs: dict) -> None:
    """
    Listens for the `user_signed_up` signal and queues background tasks to
    send the welcome email and slack invite
    """
    logger.info(f"Received user_signed_up signal for {user}")
    async_task("core.tasks.send_slack_invite_job", user.email)
    async_task("core.tasks.send_welcome_email", user.email)


@receiver(email_confirmed)
def email_confirmed_callback(email_address: EmailConfirmation, **kwargs: dict) -> None:
    """
    Listens for the `email_confirmed` signal and queues a background task to
    add the user to the mailing list
    """
    logger.info(f"Received email_confirmed signal for {email_address.email}")
    async_task("core.tasks.add_user_to_mailing_list", email_address.email)
