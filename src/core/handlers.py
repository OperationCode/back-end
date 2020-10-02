import logging
from calendar import timegm
from datetime import datetime

from allauth.account.models import EmailConfirmation
from allauth.account.signals import email_confirmed, user_signed_up
from django.conf import settings
from django.contrib.auth.models import User
from django.dispatch import receiver

from core.tasks import (
    add_user_to_mailing_list,
    send_slack_invite_job,
    send_welcome_email,
)

logger = logging.getLogger(__name__)


# noinspection PyUnresolvedReferences
def custom_jwt_payload_handler(user: User) -> dict:
    """
    Overrides the default jwt_payload_handler to embed
    extra data into the JWT
    """
    profile = user.profile

    payload = {
        "email": user.username,
        "firstName": user.first_name,
        "lastName": user.last_name,
        "zipcode": profile.zipcode,
        "isMentor": profile.is_mentor,
        "exp": datetime.utcnow() + settings.JWT_AUTH["JWT_EXPIRATION_DELTA"],
        "orig_iat": timegm(datetime.utcnow().utctimetuple()),
    }

    return payload


def get_username_from_jwt(payload: dict) -> str:
    """
    Overrides the default payload handler to use
    "email" instead of "username"
    :param payload:
    """
    return payload.get("email")


@receiver(user_signed_up)
def registration_callback(user: User, **kwargs: dict) -> None:
    """
    Listens for the `user_signed_up` signal and adds a background tasks to
    send the welcome email
    """
    logger.info(f"Received user_signed_up signal for {user}")
    send_welcome_email(user.email)


@receiver(email_confirmed)
def email_confirmed_callback(email_address: EmailConfirmation, **kwargs: dict) -> None:
    """
    Listens for the `email_confirmed` signal and adds a background task to
    add the user to the mailing list and send the slack invite
    """
    logger.info(f"Received email_confirmed signal for {email_address.email}")
    send_slack_invite_job(email_address.email)
    add_user_to_mailing_list(email_address.email)
