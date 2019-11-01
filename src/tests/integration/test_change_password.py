from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient

from tests.test_data import fake


def test_password_change_valid_params(authed_client: APIClient, user: User):
    password = fake.password()
    res = authed_client.post(
        reverse("rest_password_change"),
        {"newPassword1": password, "newPassword2": password},
    )

    assert res.status_code == 200


def test_password_change_unauthed(client: APIClient, user: User):
    password = fake.password()
    res = client.post(
        reverse("rest_password_change"),
        {"newPassword1": password, "newPassword2": password},
    )

    assert res.status_code == 401


def test_password_change_login_with_new_password(authed_client: APIClient, user: User):
    password = fake.password()

    res = authed_client.post(
        reverse("rest_password_change"),
        {"newPassword1": password, "newPassword2": password},
    )

    assert res.status_code == 200

    res = authed_client.post(
        reverse("rest_login"), {"email": user.email, "password": password}
    )

    assert res.status_code == 200


def test_password_change_common_password_error(authed_client: APIClient, user: User):
    res = authed_client.post(
        reverse("rest_password_change"),
        {"newPassword1": "password", "newPassword2": "password"},
    )

    assert res.status_code == 400
    assert "This password is too common." in res.data["new_password2"]
