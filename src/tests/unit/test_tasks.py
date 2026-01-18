from typing import List

import pytest
import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from pytest_mock import MockFixture

from core.tasks import (
    add_user_to_mailing_list,
    send_slack_invite_job,
    send_welcome_email,
)

TEST_EMAIL = "test@test.com"


@pytest.mark.django_db
def test_send_welcome_email(mailoutbox: List[EmailMultiAlternatives]):
    # Tasks are now synchronous functions, call directly
    send_welcome_email(TEST_EMAIL)

    assert len(mailoutbox) == 1
    assert TEST_EMAIL in mailoutbox[0].to
    assert mailoutbox[0].body is not None


@pytest.mark.django_db
def test_send_slack_invite_job(mocker: MockFixture):
    mock = mocker.patch.object(requests, "post")
    # Tasks are now synchronous functions, call directly
    send_slack_invite_job(TEST_EMAIL)

    assert mock.called
    assert mock.call_args[0] == (f"{settings.PYBOT_URL}/pybot/api/v1/slack/invite",)
    assert "email" in mock.call_args[1]["json"]
    assert mock.call_args[1]["json"]["email"] == TEST_EMAIL


@pytest.mark.django_db
def test_add_user_to_mailing_list(user: User, mocker: MockFixture):
    mock = mocker.patch("core.tasks.MailChimp")
    # Tasks are now synchronous functions, call directly
    add_user_to_mailing_list(user.email)

    assert mock.called
