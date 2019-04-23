import logging

import requests
from background_task import background
from django.core.mail import send_mail
from mailchimp3 import MailChimp

from operationcode_backend import settings

logger = logging.getLogger(__name__)


@background(schedule=5)
def send_welcome_email(email, message):
    print(f"Sending email with message: {message}")
    try:
        response = send_mail(
            "Subject here", message, "test@test.org", [email], fail_silently=False
        )
        print(response)
    except Exception as e:
        logger.exception("Exception trying to send welcome email to user", e)


@background(schedule=1)
def send_slack_invite_job(email):
    url = f"{settings.PYBOT_URL}/pybot/api/v1/slack/invite"
    headers = {"Authorization": f"Bearer {settings.PYBOT_AUTH_TOKEN}"}
    res = requests.post(url, json={"email": email}, headers=headers)

    logger.info("Slack invite response:", res)


@background(schedule=1)
def add_user_to_mailing_list(email: str, first_name: str, last_name: str) -> None:
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
