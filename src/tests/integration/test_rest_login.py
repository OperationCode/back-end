import pytest
from allauth.account.models import EmailAddress
from django.urls import reverse


@pytest.mark.django_db
def test_valid_rest_login(client, user):
    res = client.post(
        reverse("rest_login"), {"email": user.email, "password": user.username}
    )

    assert res.status_code == 200
    assert res.data["token"] is not None

    returned_user = res.data["user"]
    assert returned_user["username"] == user.username
    assert returned_user["email"] == user.email


@pytest.mark.django_db
def test_unverified_email_rest_login(client, user):
    EmailAddress.objects.filter(email=user.email).update(verified=False)

    res = client.post(
        reverse("rest_login"), {"email": user.email, "password": user.username}
    )

    assert res.status_code == 400
    assert "Email has not been verified" in res.data["error"]


@pytest.mark.django_db
def test_invalid_pass_rest_login(client, user):
    res = client.post(
        reverse("rest_login"), {"email": user.email, "password": "wrongPass"}
    )

    assert res.status_code == 400
    assert "The email or password you entered is incorrect!" in res.data["error"]


@pytest.mark.django_db
def test_invalid_username_rest_login(client, user):
    res = client.post(
        reverse("rest_login"), {"email": "wrong@email.com", "password": user.username}
    )

    assert res.status_code == 400
    assert "The email or password you entered is incorrect!" in res.data["error"]
