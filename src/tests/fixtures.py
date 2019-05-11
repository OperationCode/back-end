import pytest
from allauth.account.models import EmailAddress

from tests import factories as f


@pytest.fixture
def user(db):
    user = f.UserFactory.create()
    EmailAddress.objects.create(
        user=user, email=user.email, primary=True, verified=True
    )
    return user


@pytest.fixture
def register_form():
    return {
        "password1": "P4ssw0rd1",
        "password2": "P4ssw0rd1",
        "email": "user@email.com",
    }
