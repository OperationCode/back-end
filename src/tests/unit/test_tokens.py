import pytest
from core.handlers import CustomTokenObtainPairSerializer

from .. import factories as f


@pytest.mark.django_db
def test_valid_token():
    user = f.UserFactory(email="test@email.com")
    token = CustomTokenObtainPairSerializer.get_token(user)

    assert token["firstName"] == user.first_name
    assert token["lastName"] == user.last_name
    assert token["zipcode"] == user.profile.zipcode
