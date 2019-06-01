import os
from os.path import dirname, join

import pytest
from django.test import Client
from django.test.client import MULTIPART_CONTENT
from django.urls import reverse


def test_form_invalid_returns_template(client):
    response = client.post(reverse("codeschool_form"))

    assert "frontend/codeschool-form.html" in response.template_name


@pytest.mark.django_db
@pytest.mark.parametrize(
    argnames="filename, status", argvalues=[("200x200.jpg", 302), ("200x300.jpg", 200)]
)
def test_form_submission(mocker, filename, status):
    mocker.patch("frontend.views.requests.post")
    client = Client()
    os.environ["RECAPTCHA_DISABLE"] = "True"

    with open(join(dirname(dirname(__file__)), "assets", filename), "rb") as fp:
        response = client.post(
            reverse("codeschool_form"),
            data={
                "name": "Startup Institute",
                "url": "https://www.startupinstitute.com/",
                "logo": fp,
                "fullTime": True,
                "hardwareIncluded": True,
                "hasOnline": True,
                "accredited": True,
                "onlineOnly": True,
                "mooc": True,
                "isPartner": True,
                "housing": True,
                "city": "New York",
                "state": "NY",
                "country": "US",
                "zipcode": 10004,
                "rep_name": "Bob",
                "address1": "25 Broadway",
                "address2": "10th Floor",
                "rep_email": "bob@test.test",
            },
            content_type=MULTIPART_CONTENT,
        )

        assert response.status_code == status
