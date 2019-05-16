import logging

import requests
from background_task import background
from django.conf import settings
from django.contrib.auth.models import User as AuthUser
from django.core.mail import send_mail
from mailchimp3 import MailChimp

logger = logging.getLogger(__name__)


@background(schedule=0)
def send_welcome_email(email: str, message: str) -> None:
    logger.info(f"Sending email with message: {message}")
    try:
        response = send_mail(
            "Subject here", message, "test@test.org", [email], fail_silently=False
        )
        logger.info(f"Email to {email} response", response)

    except Exception as e:
        logger.exception("Exception trying to send welcome email to user", e)


@background(schedule=0)
def send_slack_invite_job(email: str) -> None:
    """
    Background task that sends pybot a request triggering an invite for
    a newly registered user

    :param email: Email the user signed up with
    """
    try:
        logger.info(f"Sending slack invite for email: {email}")
        url = f"{settings.PYBOT_URL}/pybot/api/v1/slack/invite"
        headers = {"Authorization": f"Bearer {settings.PYBOT_AUTH_TOKEN}"}
        res = requests.post(url, json={"email": email}, headers=headers)

        logger.info("Slack invite response:", res)
    except Exception:
        logger.exception(
            f"Exception while trying to send slack invite for email {email}"
        )


@background(schedule=0)
def add_user_to_mailing_list(email: str) -> None:
    """
    Adds the new user's email to our mailchimp list (which should trigger a
    welcome email)
    """
    try:
        user = AuthUser.objects.get(email=email)

        client = MailChimp(
            settings.MAILCHIMP_API_KEY, mc_user=settings.MAILCHIMP_USERNAME
        )
        res = client.lists.members.create(
            settings.MAILCHIMP_LIST_ID,
            {
                "email_address": email,
                "status": "subscribed",
                "merge_fields": {"FNAME": user.first_name, "LNAME": user.last_name},
            },
        )

        logger.info("Added user to email list.  Response: ", res)
    except Exception:
        logger.exception(f"Exception while adding email {email} to mailing list.")
