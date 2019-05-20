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


@pytest.mark.django_db
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
def test_professional_details_update(client: test.Client, authed_user: User, params):
    res = client.patch(
        reverse("update_profile"), params, content_type="application/json"
    )

    assert res.status_code == 200

    authed_user.refresh_from_db()
    profile = authed_user.profile

    for key, val in params.items():
        assert getattr(profile, key) == val


@pytest.mark.parametrize(
    argnames="method, status", argvalues=[("post", 405), ("get", 200), ("patch", 200)]
)
def test_update_requires_get_or_patch(
    client: test.Client, authed_user: User, method: str, status: int
):
    func = getattr(client, method)
    res = func(reverse("update_profile"))
    assert res.status_code == status


@pytest.mark.parametrize(
    argnames="content_type, status",
    argvalues=[
        ("application/octet-stream", 415),
        ("text/html", 415),
        ("multipart/form-data", 200),
        ("application/json", 200),
    ],
)
def test_update_requires_application_json_or_multipart(
    client: test.Client, authed_user: User, content_type: str, status: int
):
    res = client.patch(
        reverse("update_profile"), professional_details, content_type=content_type
    )

    assert res.status_code == status
