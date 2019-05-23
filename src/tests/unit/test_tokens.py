import pytest

from core.handlers import custom_jwt_payload_handler

from .. import factories as f


def test_valid_token():
    user = f.UserFactory.build(email="test@email.com")
    token = custom_jwt_payload_handler(user)

    assert token["firstName"] == user.first_name
    assert token["lastName"] == user.last_name
    assert token["zipcode"] == user.profile.zip
