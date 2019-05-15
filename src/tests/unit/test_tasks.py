import pytest
import requests
from django.conf import settings

from core.tasks import (
    send_welcome_email,
    send_slack_invite_job,
    add_user_to_mailing_list,
)

from background_task.tasks import tasks

TEST_EMAIL = "test@test.test"


def mocked_run_next_task(queue=None):
    """
    We mock tasks.mocked_run_next_task to give other threads some time to update the database.
    Otherwise we run into a locked database.
    """
    return tasks.run_next_task(queue)


run_next_task = mocked_run_next_task


@pytest.mark.django_db
def test_send_welcome_email(mailoutbox):
    send_welcome_email(TEST_EMAIL, "test")
    run_next_task()

    assert len(mailoutbox) == 1
    assert TEST_EMAIL in mailoutbox[0].to
    assert mailoutbox[0].body == "test"


@pytest.mark.django_db
def test_send_slack_invite_job(mocker):
    mock = mocker.patch.object(requests, "post")
    send_slack_invite_job(TEST_EMAIL)

    run_next_task()

    assert mock.called
    assert mock.call_args[0] == (f"{settings.PYBOT_URL}/pybot/api/v1/slack/invite",)
    assert "email" in mock.call_args[1]["json"]
    assert mock.call_args[1]["json"]["email"] == TEST_EMAIL


@pytest.mark.django_db
def test_add_user_to_mailing_list(user, mocker):
    mock = mocker.patch("core.tasks.MailChimp")
    add_user_to_mailing_list(user.email)

    run_next_task()

    assert mock.called
