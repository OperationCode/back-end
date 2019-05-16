from typing import Dict

import pytest
from allauth.account.models import EmailAddress
from django.contrib.auth.models import User

from tests import factories as f


@pytest.fixture
def user(db) -> User:
    user = f.UserFactory.create()
    EmailAddress.objects.create(
        user=user, email=user.email, primary=True, verified=True
    )
    return user


@pytest.fixture
def register_form() -> Dict[str, str]:
    return {
        "password1": "P4ssw0rd1",
        "password2": "P4ssw0rd1",
        "email": "user@email.com",
        "firstName": "Test",
        "lastName": "Testerson",
        "zip": "12345",
    }
