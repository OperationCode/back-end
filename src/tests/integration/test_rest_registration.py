from typing import Dict, List

import pytest
from allauth.account.models import EmailAddress, EmailConfirmation
from background_task.models import Task as BackgroundTask
from django import test
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.test.utils import override_settings
from django.urls import reverse


@pytest.mark.django_db
def test_confirmation_email_sent(
    client: test.Client,
    register_form: Dict[str, str],
    mailoutbox: List[EmailMultiAlternatives],
):
    res = client.post(reverse("rest_register"), register_form)

    assert res.status_code == 201
    assert len(mailoutbox) == 1
    assert register_form["email"] in mailoutbox[0].to


@pytest.mark.django_db
def test_user_is_created(client: test.Client, register_form):
    res = client.post(reverse("rest_register"), register_form)

    assert res.status_code == 201

    users = get_user_model().objects.all()

    assert len(users) == 1
    user = users[0]

    assert user.email == register_form["email"]
    assert user.first_name == register_form["firstName"]
    assert user.last_name == register_form["lastName"]


@pytest.mark.django_db
def test_user_profile_created(client: test.Client, register_form):
    res = client.post(reverse("rest_register"), register_form)

    assert res.status_code == 201

    users = get_user_model().objects.all()

    assert len(users) == 1

    profile = users[0].profile
    assert profile.zip == register_form["zip"]


@pytest.mark.django_db
def test_slack_invite_task_created(
    client: test.Client,
    register_form: Dict[str, str],
    mailoutbox: List[EmailMultiAlternatives],
):
    res = client.post(reverse("rest_register"), register_form)

    assert res.status_code == 201

    tasks = BackgroundTask.objects.all()

    assert len(tasks) == 1
    assert tasks[0].task_name.split(".")[-1] == "send_slack_invite_job"


@pytest.mark.django_db
def test_already_used_email(
    client: test.Client,
    mailoutbox: List[EmailMultiAlternatives],
    register_form: Dict[str, str],
    user,
):
    register_form["email"] = user.email
    res = client.post(reverse("rest_register"), register_form)

    assert res.status_code == 400
    assert res.data["email"]


@pytest.mark.django_db
def test_not_matching_passwords(
    client: test.Client, mailoutbox: List[EmailMultiAlternatives], register_form
):
    register_form["password2"] = "different"
    res = client.post(reverse("rest_register"), register_form)

    assert res.status_code == 400
    assert "The two password fields didn't match." in res.data["non_field_errors"]


@override_settings(ACCOUNT_EMAIL_CONFIRMATION_HMAC=False)
@pytest.mark.django_db
def test_email_verification_token(
    client: test.Client,
    register_form: Dict[str, str],
    mailoutbox: List[EmailMultiAlternatives],
):
    client.post(reverse("rest_register"), register_form)
    email_conf = EmailConfirmation.objects.get(
        email_address__email=register_form["email"]
    )

    res = client.post(reverse("rest_verify_email"), {"key": email_conf.key})

    assert res.status_code == 200
    assert res.data["detail"] == "ok"

    email = EmailAddress.objects.get(email=register_form["email"])
    assert email.verified


@pytest.mark.django_db
def test_email_verification_with_invalid_token(
    client: test.Client,
    register_form: Dict[str, str],
    mailoutbox: List[EmailMultiAlternatives],
):
    res = client.post(reverse("rest_verify_email"), {"key": "abc123"})

    assert res.status_code == 404
    assert res.data["detail"] == "Not found."


@pytest.mark.django_db
@override_settings(ACCOUNT_EMAIL_CONFIRMATION_HMAC=False)
def test_mailing_list_task_created(
    client: test.Client,
    register_form: Dict[str, str],
    mailoutbox: List[EmailMultiAlternatives],
):
    client.post(reverse("rest_register"), register_form)
    email_conf = EmailConfirmation.objects.get(
        email_address__email=register_form["email"]
    )

    res = client.post(reverse("rest_verify_email"), {"key": email_conf.key})

    assert res.status_code == 200
    tasks = BackgroundTask.objects.all()

    assert len(tasks) == 2
    assert any(
        task.task_name.split(".")[-1] == "add_user_to_mailing_list" for task in tasks
    )
