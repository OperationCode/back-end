import re
from typing import List

from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.test import Client
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APIClient

from tests.test_data import fake

# dj-rest-auth uses path segments for password reset confirm: /confirm/{uid}/{token}/
token_pattern = re.compile(r"http.*/confirm/(?P<uid>[^/]+)/(?P<token>[^/]+)/")


def test_password_reset_sends_email(
    client: APIClient, user: User, mailoutbox: List[EmailMultiAlternatives]
):
    res = client.post(reverse("rest_password_reset"), {"email": user.email})

    assert res.status_code == 200
    assert len(mailoutbox) == 1

    groups = token_pattern.search(mailoutbox[0].body).groupdict()

    assert groups["uid"]
    assert groups["token"]


def test_password_reset_invalid_email(
    client: APIClient, user: User, mailoutbox: List[EmailMultiAlternatives]
):
    res = client.post(reverse("rest_password_reset"), {"email": "bad@email"})

    assert res.status_code == 400
    assert len(mailoutbox) == 0


def test_password_reset_confirm(
    client: APIClient, user: User, mailoutbox: List[EmailMultiAlternatives]
):
    # First request a password reset to get a valid token
    client.post(reverse("rest_password_reset"), {"email": user.email})

    # Extract uid and token from the email
    groups = token_pattern.search(mailoutbox[0].body).groupdict()
    uid = groups["uid"]
    token = groups["token"]
    password = fake.password()

    res = client.post(
        reverse("rest_password_reset_confirm"),
        {
            "new_password1": password,
            "new_password2": password,
            "token": token,
            "uid": uid,
        },
    )

    assert res.status_code == 200


def test_password_reset_confirm_bad_token(client: APIClient, user: User):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    password = fake.password()

    res = client.post(
        reverse("rest_password_reset_confirm"),
        {
            "new_password1": password,
            "new_password2": password,
            "token": "badToken",
            "uid": uid,
        },
    )

    assert res.status_code == 400
    error = res.data["error"]
    assert error == "Could not reset password.  Reset token expired or invalid."


def test_password_reset_login_with_new_password(
    client: APIClient, user: User, mailoutbox: List[EmailMultiAlternatives]
):
    # First request a password reset to get a valid token
    client.post(reverse("rest_password_reset"), {"email": user.email})

    # Extract uid and token from the email
    groups = token_pattern.search(mailoutbox[0].body).groupdict()
    uid = groups["uid"]
    token = groups["token"]
    password = fake.password()

    res = client.post(
        reverse("rest_password_reset_confirm"),
        {
            "new_password1": password,
            "new_password2": password,
            "token": token,
            "uid": uid,
        },
    )

    assert res.status_code == 200

    res = client.post(
        reverse("rest_login"), {"email": user.email, "password": password}
    )

    assert res.status_code == 200


def test_password_reset_common_password_error(
    client: APIClient, user: User, mailoutbox: List[EmailMultiAlternatives]
):
    # First request a password reset to get a valid token
    client.post(reverse("rest_password_reset"), {"email": user.email})

    # Extract uid and token from the email
    groups = token_pattern.search(mailoutbox[0].body).groupdict()
    uid = groups["uid"]
    token = groups["token"]

    res = client.post(
        reverse("rest_password_reset_confirm"),
        {
            "new_password1": "password",
            "new_password2": "password",
            "token": token,
            "uid": uid,
        },
    )

    assert res.status_code == 400
    assert res.data["error"] == "This password is too common."


def test_password_reset_html_form_loads(
    client: APIClient, user: User, mailoutbox: List[EmailMultiAlternatives]
):
    """Test that the HTML password reset form loads correctly."""
    # Request a password reset to get a valid token
    api_client = client
    api_client.post(reverse("rest_password_reset"), {"email": user.email})

    # Extract uid and token from the email
    groups = token_pattern.search(mailoutbox[0].body).groupdict()
    uid = groups["uid"]
    token = groups["token"]

    # Use Django test client (not DRF APIClient) for HTML form
    django_client = Client()

    # GET the password reset confirm page (follow redirects to see the form)
    url = reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": token})
    response = django_client.get(url, follow=True)

    assert response.status_code == 200
    # Check that the form is present (not the "Invalid Reset Link" message)
    assert b"Reset Your Password" in response.content
    assert b"Invalid Reset Link" not in response.content
    assert b"new_password" in response.content


def test_password_reset_html_form_submission(
    client: APIClient, user: User, mailoutbox: List[EmailMultiAlternatives]
):
    """Test that the HTML password reset form can be submitted successfully."""
    # Request a password reset to get a valid token
    api_client = client
    api_client.post(reverse("rest_password_reset"), {"email": user.email})

    # Extract uid and token from the email
    groups = token_pattern.search(mailoutbox[0].body).groupdict()
    uid = groups["uid"]
    token = groups["token"]

    # Use Django test client for HTML form
    django_client = Client()

    # GET the password reset confirm page (this validates the token and redirects)
    # Django's PasswordResetConfirmView validates the token on GET and redirects to
    # a '/set-password/' URL where the actual form is displayed
    url = reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": token})
    response = django_client.get(url, follow=True)

    assert response.status_code == 200

    # The redirected URL should contain the form
    final_url = response.redirect_chain[-1][0] if response.redirect_chain else url

    # POST the new password to the final URL
    new_password = fake.password()
    response = django_client.post(
        final_url,
        {
            "new_password1": new_password,
            "new_password2": new_password,
        },
        follow=True,
    )

    # Should redirect to success page
    assert response.status_code == 200
    assert (
        b"Password Reset Complete" in response.content
        or b"success" in response.content.lower()
    )

    # Verify we can log in with the new password
    login_response = api_client.post(
        reverse("rest_login"), {"email": user.email, "password": new_password}
    )
    assert login_response.status_code == 200
