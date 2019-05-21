import pytest
from django import test
from django.contrib.auth.models import User
from django.urls import reverse

from tests.integration.test_data import (
    empty_update,
    interests_empty,
    interests_multiple,
    interests_single,
    military_details,
    military_status,
    professional_details,
)


@pytest.mark.parametrize(
    argnames="params",
    argvalues=[
        empty_update,
        professional_details,
        military_status,
        military_details,
        interests_empty,
        interests_single,
        interests_multiple,
    ],
    ids=[
        "empty_update",
        "professional_details",
        "military_status",
        "military_details",
        "interests_empty",
        "interests_single",
        "interests_multiple",
    ],
)
def test_professional_details_update(
    authed_client: test.Client, authed_user: User, params
):
    res = authed_client.patch(reverse("update_profile"), params)

    assert res.status_code == 200

    authed_user.refresh_from_db()
    profile = authed_user.profile

    for key, val in params.items():
        assert getattr(profile, key) == val


@pytest.mark.parametrize(
    argnames="method, status", argvalues=[("post", 405), ("get", 200), ("patch", 200)]
)
def test_update_requires_get_or_patch(
    authed_client: test.Client, method: str, status: int
):
    func = getattr(authed_client, method)
    res = func(reverse("update_profile"))
    assert res.status_code == status


@pytest.mark.parametrize(
    argnames="content_type, status",
    argvalues=[("application/octet-stream", 415), ("text/html", 415)],
)
def test_update_requires_correct_format(
    authed_client: test.Client, content_type: str, status: int
):
    res = authed_client.patch(
        reverse("update_profile"), professional_details, content_type=content_type
    )

    assert res.status_code == status
