import humps
import pytest
from django import test
from django.contrib.auth.models import User
from django.urls import reverse


def test_profile_updates_correctly(
    profile_admin_client: test.Client, user: User, update_profile_params
):
    url = f"{reverse('admin_update_profile')}?email={user.email}"
    res = profile_admin_client.patch(url, humps.camelize(update_profile_params))

    assert res.status_code == 200

    user.refresh_from_db()
    profile = user.profile

    for key, val in update_profile_params.items():
        assert getattr(profile, key) == val


@pytest.mark.parametrize(
    argnames="method, status",
    argvalues=[("get", 400), ("put", 400), ("post", 405), ("patch", 400)],
)
def test_requires_query_param(
    profile_admin_client: test.Client, method: str, status: int
):
    request_method = getattr(profile_admin_client, method)
    url = f"{reverse('admin_update_profile')}"
    res = request_method(url)

    assert res.status_code == status


def test_missing_profile_returns_404(profile_admin_client: test.Client):
    url = f"{reverse('admin_update_profile')}?email=abc"
    res = profile_admin_client.get(url)

    assert res.status_code == 404


@pytest.mark.parametrize(
    argnames="method, status", argvalues=[("get", 200), ("post", 405), ("patch", 200)]
)
def test_staff_user_has_access(
    authed_admin_client: test.Client, user: User, method: str, status: int
):
    request_method = getattr(authed_admin_client, method)
    url = f"{reverse('admin_update_profile')}?email={user.email}"
    res = request_method(url)

    assert res.status_code == status


@pytest.mark.parametrize(
    argnames="method, status",
    argvalues=[("get", 403), ("put", 403), ("post", 405), ("patch", 403)],
)
def test_view_requires_profile_admin_group(
    authed_client: test.Client, user: User, method: str, status: int
):
    request_method = getattr(authed_client, method)
    url = f"{reverse('admin_update_profile')}?email={user.email}"
    res = request_method(url)

    assert res.status_code == status
