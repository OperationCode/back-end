import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient


def test_user_api_required_auth(authed_client: APIClient, user: User):
    res = authed_client.get(reverse("view_user"))

    assert res.status_code == 200

    assert res.data["first_name"] == user.first_name


def test_user_api_returns_correct_data(authed_client: APIClient, user: User):
    res = authed_client.get(reverse("view_user"))

    assert res.status_code == 200

    assert res.data["last_name"] == user.last_name
    assert res.data["email"] == user.email
    assert res.data["username"] == user.username
    assert res.data["zipcode"] == user.profile.zipcode
    assert res.data["sign_in_count"] == user.profile.sign_in_count
    assert res.data["is_mentor"] == user.profile.is_mentor
    assert res.data["state"] == user.profile.state
    assert res.data["address_1"] == user.profile.address_1
    assert res.data["address_2"] == user.profile.address_2
    assert res.data["city"] == user.profile.city
    assert res.data["branch_of_service"] == user.profile.branch_of_service
    assert res.data["years_of_service"] == user.profile.years_of_service
    assert res.data["pay_grade"] == user.profile.pay_grade

    specialty = res.data["military_occupational_specialty"]
    assert specialty == user.profile.military_occupational_specialty


@pytest.mark.parametrize(
    argnames="method, status", argvalues=[("post", 405), ("get", 200), ("patch", 200)]
)
def test_user_api_requires_get_or_patch(
    authed_client: APIClient, method: str, status: int
):
    func = getattr(authed_client, method)
    res = func(reverse("view_user"))
    assert res.status_code == status
