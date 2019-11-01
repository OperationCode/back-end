import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_unauthenticated_get_successful(client):
    res = client.get(reverse("codeschool-list"))

    assert res.status_code == 200


@pytest.mark.parametrize(
    argnames="method", argvalues=["post", "put", "patch", "delete"]
)
def test_only_allow_get_method(client, method):
    func = getattr(client, method)
    res = func(reverse("codeschool-list"))

    assert res.status_code == 405
