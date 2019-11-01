from typing import List

import pytest
import requests
from background_task.tasks import tasks
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


def mocked_run_next_task(queue=None):
    """
    We mock tasks.mocked_run_next_task to give other threads some time to update the database.
    Otherwise we run into a locked database.
    """
    return tasks.run_next_task(queue)


run_next_task = mocked_run_next_task


@pytest.mark.django_db
def test_send_welcome_email(mailoutbox: List[EmailMultiAlternatives]):
    send_welcome_email(TEST_EMAIL)
    run_next_task()

    assert len(mailoutbox) == 1
    assert TEST_EMAIL in mailoutbox[0].to
    assert mailoutbox[0].body is not None


@pytest.mark.django_db
def test_send_slack_invite_job(mocker: MockFixture):
    mock = mocker.patch.object(requests, "post")
    send_slack_invite_job(TEST_EMAIL)

    run_next_task()

    assert mock.called
    assert mock.call_args[0] == (f"{settings.PYBOT_URL}/pybot/api/v1/slack/invite",)
    assert "email" in mock.call_args[1]["json"]
    assert mock.call_args[1]["json"]["email"] == TEST_EMAIL


@pytest.mark.django_db
def test_add_user_to_mailing_list(user: User, mocker: MockFixture):
    mock = mocker.patch("core.tasks.MailChimp")
    add_user_to_mailing_list(user.email)

    run_next_task()

    assert mock.called
