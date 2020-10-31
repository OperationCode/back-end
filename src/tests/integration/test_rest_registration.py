import re
from typing import Dict, List

import pytest
from allauth.account.models import EmailAddress
from background_task.models import Task as BackgroundTask
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponseNotFound
from django.urls import reverse
from rest_framework.test import APIClient

key_pattern = re.compile(r"http.+/confirm_email\?key=(?P<key>.+)")


@pytest.mark.django_db
def test_confirmation_email_sent(
    client: APIClient,
    register_form: Dict[str, str],
    mailoutbox: List[EmailMultiAlternatives],
):
    res = client.post(reverse("rest_register"), register_form)

    assert res.status_code == 201
    assert len(mailoutbox) == 1
    assert register_form["email"] in mailoutbox[0].to


@pytest.mark.django_db
def test_user_is_created(client: APIClient, register_form: Dict[str, str]):
    res = client.post(reverse("rest_register"), register_form)

    assert res.status_code == 201

    users = User.objects.all()

    assert len(users) == 1
    user = users[0]

    assert user.email == register_form["email"]
    assert user.first_name == register_form["firstName"]
    assert user.last_name == register_form["lastName"]


@pytest.mark.django_db
def test_user_profile_created(client: APIClient, register_form: Dict[str, str]):
    res = client.post(reverse("rest_register"), register_form)

    assert res.status_code == 201

    users = User.objects.all()

    assert len(users) == 1

    profile = users[0].profile
    assert profile.zipcode == register_form["zipcode"]


@pytest.mark.django_db
def test_slack_invite_task_created(
        client: APIClient,
        register_form: Dict[str, str],
        mailoutbox: List[EmailMultiAlternatives],
):
    client.post(reverse("rest_register"), register_form)

    body = mailoutbox[0].body
    groups = key_pattern.search(body).groupdict()

    res = client.post(reverse("rest_verify_email"), {"key": groups["key"]})

    assert res.status_code == 200
    assert res.data["detail"] == "ok"

    email = EmailAddress.objects.get(email=register_form["email"])
    assert email.verified

    tasks = BackgroundTask.objects.filter(task_name="core.tasks.send_slack_invite_job")

    assert len(tasks) == 1
    assert tasks[0].task_name.split(".")[-1] == "send_slack_invite_job"


@pytest.mark.django_db
def test_already_used_email(
    client: APIClient,
    mailoutbox: List[EmailMultiAlternatives],
    register_form: Dict[str, str],
    user,
):
    register_form["email"] = user.email
    res = client.post(reverse("rest_register"), register_form)

    assert res.status_code == 400
    assert res.data["email"]


@pytest.mark.django_db
def test_email_verification_token(
    client: APIClient,
    register_form: Dict[str, str],
    mailoutbox: List[EmailMultiAlternatives],
):
    client.post(reverse("rest_register"), register_form)

    body = mailoutbox[0].body
    groups = key_pattern.search(body).groupdict()

    res = client.post(reverse("rest_verify_email"), {"key": groups["key"]})

    assert res.status_code == 200
    assert res.data["detail"] == "ok"

    email = EmailAddress.objects.get(email=register_form["email"])
    assert email.verified


@pytest.mark.django_db
def test_email_verification_with_invalid_token(
    client: APIClient,
    register_form: Dict[str, str],
    mailoutbox: List[EmailMultiAlternatives],
):
    res = client.post(reverse("rest_verify_email"), {"key": "abc123"})

    assert res.status_code == 404
    assert isinstance(res, HttpResponseNotFound)


@pytest.mark.django_db
def test_mailing_list_task_created(
    client: APIClient,
    register_form: Dict[str, str],
    mailoutbox: List[EmailMultiAlternatives],
):
    client.post(reverse("rest_register"), register_form)

    body = mailoutbox[0].body
    groups = key_pattern.search(body).groupdict()

    res = client.post(reverse("rest_verify_email"), {"key": groups["key"]})

    assert res.status_code == 200
    tasks = BackgroundTask.objects.filter(
        task_name="core.tasks.add_user_to_mailing_list"
    )

    assert len(tasks) == 1
    assert any(
        task.task_name.split(".")[-1] == "add_user_to_mailing_list" for task in tasks
    )
