import pytest
import re
from django.urls import reverse

token_pattern = re.compile("http.*/reset/(?P<uid>.+?)/(?P<token>.+?)/")


@pytest.mark.django_db
def test_password_reset_sends_email(client, user, mailoutbox):
    res = client.post(reverse("rest_password_reset"), {"email": user.email})

    assert res.status_code == 200
    assert len(mailoutbox) == 1

    groups = token_pattern.search(mailoutbox[0].body).groupdict()

    assert groups["uid"]
    assert groups["token"]


@pytest.mark.django_db
def test_password_reset_invalid_email(client, user, mailoutbox):
    res = client.post(reverse("rest_password_reset"), {"email": "bad@email"})

    assert res.status_code == 400
    assert len(mailoutbox) == 0
