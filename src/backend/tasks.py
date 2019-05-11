import logging

import requests
from background_task import background
from django.conf import settings
from django.core.mail import send_mail
from mailchimp3 import MailChimp

logger = logging.getLogger(__name__)


@background(schedule=5)
def send_welcome_email(email: str, message: str) -> None:
    logger.info(f"Sending email with message: {message}")
    try:
        response = send_mail(
            "Subject here", message, "test@test.org", [email], fail_silently=False
        )
        logger.info(f"Email to {email} response", response)

    except Exception as e:
        logger.exception("Exception trying to send welcome email to user", e)


@background(schedule=1)
def send_slack_invite_job(email: str) -> None:
    """
    Sends pybot a request triggering an invite for the newly
    registered user

    :param email: Email the user signed up with
    """
    logger.info(f"Sending slack invite for email: {email}")
    url = f"{settings.PYBOT_URL}/pybot/api/v1/slack/invite"
    headers = {"Authorization": f"Bearer {settings.PYBOT_AUTH_TOKEN}"}
    res = requests.post(url, json={"email": email}, headers=headers)

    logger.info("Slack invite response:", res)


@background(schedule=1)
def add_user_to_mailing_list(email: str, first_name: str, last_name: str) -> None:
    """
    Adds the new user's email to our mailchimp list (which should trigger a
    welcome email)
    """
    client = MailChimp(settings.MAILCHIMP_API_KEY, mc_user=settings.MAILCHIMP_USERNAME)
    res = client.lists.members.create(
        settings.MAILCHIMP_LIST_ID,
        {
            "email_address": email,
            "status": "subscribed",
            "merge_fields": {"FNAME": first_name, "LNAME": last_name},
        },
    )

    logger.info("Added user to email list.  Response: ", res)
