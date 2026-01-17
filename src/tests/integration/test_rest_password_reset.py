import re
from typing import List

from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APIClient

from tests.test_data import fake

# dj-rest-auth uses path segments for password reset confirm: /confirm/{uid}/{token}/
token_pattern = re.compile(r"http.*/confirm/(?P<uid>[^/]+)/(?P<token>[^/]+)/")


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


def test_password_reset_confirm(
    client: APIClient, user: User, mailoutbox: List[EmailMultiAlternatives]
):
    # First request a password reset to get a valid token
    client.post(reverse("rest_password_reset"), {"email": user.email})

    # Extract uid and token from the email
    groups = token_pattern.search(mailoutbox[0].body).groupdict()
    uid = groups["uid"]
    token = groups["token"]
    password = fake.password()

    res = client.post(
        reverse("rest_password_reset_confirm"),
        {
            "new_password1": password,
            "new_password2": password,
            "token": token,
            "uid": uid,
        },
    )

    assert res.status_code == 200


def test_password_reset_confirm_bad_token(client: APIClient, user: User):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    password = fake.password()

    res = client.post(
        reverse("rest_password_reset_confirm"),
        {
            "new_password1": password,
            "new_password2": password,
            "token": "badToken",
            "uid": uid,
        },
    )

    assert res.status_code == 400
    error = res.data["error"]
    assert error == "Could not reset password.  Reset token expired or invalid."


def test_password_reset_login_with_new_password(
    client: APIClient, user: User, mailoutbox: List[EmailMultiAlternatives]
):
    # First request a password reset to get a valid token
    client.post(reverse("rest_password_reset"), {"email": user.email})

    # Extract uid and token from the email
    groups = token_pattern.search(mailoutbox[0].body).groupdict()
    uid = groups["uid"]
    token = groups["token"]
    password = fake.password()

    res = client.post(
        reverse("rest_password_reset_confirm"),
        {
            "new_password1": password,
            "new_password2": password,
            "token": token,
            "uid": uid,
        },
    )

    assert res.status_code == 200

    res = client.post(
        reverse("rest_login"), {"email": user.email, "password": password}
    )

    assert res.status_code == 200


def test_password_reset_common_password_error(
    client: APIClient, user: User, mailoutbox: List[EmailMultiAlternatives]
):
    # First request a password reset to get a valid token
    client.post(reverse("rest_password_reset"), {"email": user.email})

    # Extract uid and token from the email
    groups = token_pattern.search(mailoutbox[0].body).groupdict()
    uid = groups["uid"]
    token = groups["token"]

    res = client.post(
        reverse("rest_password_reset_confirm"),
        {
            "new_password1": "password",
            "new_password2": "password",
            "token": token,
            "uid": uid,
        },
    )

    assert res.status_code == 400
    assert res.data["error"] == "This password is too common."
