import humps
import pytest
from django import test
from django.contrib.auth.models import User
from django.urls import reverse


def test_update_profile_random_params(
    authed_client: test.Client, user: User, random_profile_dict
):
    res = authed_client.patch(
        reverse("update_profile"), humps.camelize(random_profile_dict)
    )

    assert res.status_code == 200

    user.refresh_from_db()
    profile = user.profile

    for key, val in random_profile_dict.items():
        assert getattr(profile, key) == val


def test_update_profile_frontend_params(
    authed_client: test.Client, user: User, update_profile_params
):
    res = authed_client.patch(
        reverse("update_profile"), humps.camelize(update_profile_params)
    )

    assert res.status_code == 200

    user.refresh_from_db()
    profile = user.profile

    for key, val in update_profile_params.items():
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
    authed_client: test.Client, content_type: str, status: int, update_profile_params
):
    res = authed_client.patch(
        reverse("update_profile"), update_profile_params, content_type=content_type
    )

    assert res.status_code == status
