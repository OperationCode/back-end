from typing import Dict

import pytest
from allauth.account.models import EmailAddress
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_jwt.settings import api_settings

from tests import factories as f

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


@pytest.fixture
def client() -> APIClient:
    return APIClient()


@pytest.fixture
def user(db) -> User:
    user = f.UserFactory.create()
    EmailAddress.objects.create(
        user=user, email=user.email, primary=True, verified=True
    )
    return user


@pytest.fixture
def authed_user(client, user: User) -> User:
    """
    Returns a standard user that has a valid active session
    """
    # client.login(email=user.email, password=user.username)
    return user


@pytest.fixture
def authed_client(client, user: User):
    payload = jwt_payload_handler(user)
    jwt = jwt_encode_handler(payload)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {jwt}")
    return client


@pytest.fixture
def register_form() -> Dict[str, str]:
    return {
        "password": "P4ssw0rd1",
        "email": "user@email.com",
        "firstName": "Test",
        "lastName": "Testerson",
        "zip": "12345",
    }
