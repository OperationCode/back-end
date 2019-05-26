import re
from typing import List

from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APIClient

from tests.test_data import fake

token_pattern = re.compile(r"http.*/confirm\?uid=(?P<uid>.+?)&token=(?P<token>.+)")


def test_password_reset_sends_email(
    client: APIClient, user: User, mailoutbox: List[EmailMultiAlternatives]
):
    res = client.post(reverse("rest_password_reset"), {"email": user.email})

    assert res.status_code == 200
    assert len(mailoutbox) == 1

    groups = token_pattern.search(mailoutbox[0].body).groupdict()

    assert groups["uid"]
    assert groups["token"]


def test_password_reset_invalid_email(
    client: APIClient, user: User, mailoutbox: List[EmailMultiAlternatives]
):
    res = client.post(reverse("rest_password_reset"), {"email": "bad@email"})

    assert res.status_code == 400
    assert len(mailoutbox) == 0


def test_password_reset_confirm(client: APIClient, user: User):
    token = PasswordResetTokenGenerator().make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    password = fake.password()

    res = client.post(
        reverse("password_reset_confirm"),
        {
            "newPassword1": password,
            "newPassword2": password,
            "token": token,
            "uid": uid,
        },
    )

    assert res.status_code == 200


def test_password_reset_confirm_bad_token(client: APIClient, user: User):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    password = fake.password()

    res = client.post(
        reverse("password_reset_confirm"),
        {
            "newPassword1": password,
            "newPassword2": password,
            "token": "badToken",
            "uid": uid,
        },
    )

    assert res.status_code == 400
    assert "token" in res.data


def test_password_reset_login_with_new_password(client: APIClient, user: User):
    token = PasswordResetTokenGenerator().make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    password = fake.password()

    res = client.post(
        reverse("password_reset_confirm"),
        {
            "newPassword1": password,
            "newPassword2": password,
            "token": token,
            "uid": uid,
        },
    )

    assert res.status_code == 200

    res = client.post(
        reverse("rest_login"), {"email": user.email, "password": password}
    )

    assert res.status_code == 200


def test_password_reset_common_password_error(client: APIClient, user: User):
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    res = client.post(
        reverse("password_reset_confirm"),
        {
            "newPassword1": "password",
            "newPassword2": "password",
            "token": "badToken",
            "uid": uid,
        },
    )

    assert res.status_code == 400
    assert "new_password2" in res.data
