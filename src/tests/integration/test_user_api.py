import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from tests.utils import FLATTENED_USER


def test_user_api_required_auth(authed_client: APIClient):
    res = authed_client.get(reverse("view_user"))

    assert res.status_code == 200

    user_data = res.data
    for key, val in FLATTENED_USER.items():
        assert user_data[key] == val


def test_user_api_returns_correct_data(authed_client: APIClient):
    res = authed_client.get(reverse("view_user"))

    assert res.status_code == 200

    user_data = res.data
    for key, val in FLATTENED_USER.items():
        assert user_data[key] == val


@pytest.mark.parametrize(
    argnames="method, status", argvalues=[("post", 405), ("get", 200), ("patch", 200)]
)
def test_user_api_requires_get_or_patch(
    authed_client: APIClient, method: str, status: int
):
    func = getattr(authed_client, method)
    res = func(reverse("view_user"))
    assert res.status_code == status
