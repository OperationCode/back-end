import pytest

from core.handlers import custom_jwt_payload_handler
from tests.utils import DEFAULT_USER

from .. import factories as f


@pytest.mark.django_db
def test_valid_token():
    user = f.UserFactory.create(email="test@email.com")
    token = custom_jwt_payload_handler(user)

    assert token["firstName"] == DEFAULT_USER["first_name"]
    assert token["lastName"] == DEFAULT_USER["last_name"]
    assert token["zipcode"] == DEFAULT_USER["profile"]["zip"]
