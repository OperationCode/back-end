import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient

from tests.test_data import DEFAULT_PASSWORD


@pytest.mark.django_db
def test_valid_rest_login(client: APIClient, user: User):
    res = client.post(
        reverse("rest_login"), {"email": user.email, "password": DEFAULT_PASSWORD}
    )

    assert res.status_code == 200
    assert res.data["token"] is not None

    returned_user = res.data["user"]
    assert returned_user["username"] == user.email
    assert returned_user["email"] == user.email
    assert returned_user["first_name"] == user.first_name
    assert returned_user["last_name"] == user.last_name
    assert returned_user["zip"] == user.profile.zip


# Commented out until email confirmation is required again
#
# @pytest.mark.django_db
# def test_unverified_email_rest_login(client: test.Client, user: User):
#     EmailAddress.objects.filter(email=user.email).update(verified=False)
#
#     res = client.post(
#         reverse("rest_login"), {"email": user.email, "password": user.username}
#     )
#
#     assert res.status_code == 400
#     assert "Email has not been verified" in res.data["error"]


@pytest.mark.django_db
def test_invalid_pass_rest_login(client: APIClient, user: User):
    res = client.post(
        reverse("rest_login"), {"email": user.email, "password": "wrongPass"}
    )

    assert res.status_code == 401
    assert "The email or password you entered is incorrect!" in res.data["error"]


@pytest.mark.django_db
def test_invalid_username_rest_login(client: APIClient, user: User):
    res = client.post(
        reverse("rest_login"), {"email": "wrong@email.com", "password": user.username}
    )

    assert res.status_code == 401
    assert "The email or password you entered is incorrect!" in res.data["error"]
