from calendar import timegm
from datetime import datetime

from allauth.account.signals import user_signed_up
from django.conf import settings
from django.contrib.auth.models import User as AuthUser
from django.dispatch import receiver

from backend.tasks import send_slack_invite_job


# noinspection PyUnresolvedReferences
def custom_jwt_payload_handler(user: AuthUser) -> dict:
    """
    Overrides the default jwt_payload_handler to embed
    extra data into the JWT
    """
    user_info = user.userinfo

    payload = {
        "email": user.username,
        "firstName": user.first_name,
        "lastName": user.last_name,
        "zipcode": user_info.zip,
        "isMentor": user_info.mentor,
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
def registration_callback(request, user, **kwargs):
    print("*****************")
    send_slack_invite_job(user.email)
