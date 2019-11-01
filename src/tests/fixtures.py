from typing import Dict

import factory
import pytest
from django.contrib.auth.models import Group, User
from rest_framework.test import APIClient
from rest_framework_jwt.settings import api_settings

from tests import factories as f
from tests import test_data as data

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


@pytest.fixture
def client() -> APIClient:
    return APIClient()


@pytest.fixture
def user(db) -> User:
    user = f.UserFactory()
    return user


@pytest.fixture
def profile_admin_group(db) -> Group:
    group = Group(name="ProfileAdmin")
    group.save()
    return group


@pytest.fixture
def profile_admin(user: User, profile_admin_group: Group) -> User:
    user.groups.add(profile_admin_group)
    user.save()
    return user


@pytest.fixture
def authed_client(client, user: User):
    payload = jwt_payload_handler(user)
    jwt = jwt_encode_handler(payload)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {jwt}")
    return client


@pytest.fixture
def authed_admin_client(client, admin_user: User):
    payload = jwt_payload_handler(admin_user)
    jwt = jwt_encode_handler(payload)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {jwt}")
    return client


@pytest.fixture
def profile_admin_client(client, profile_admin: User):
    payload = jwt_payload_handler(profile_admin)
    jwt = jwt_encode_handler(payload)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {jwt}")
    return client


@pytest.fixture
def register_form() -> Dict[str, str]:
    user = f.UserFactory.build()

    return {
        "password": data.DEFAULT_PASSWORD,
        "email": user.email,
        "firstName": user.first_name,
        "lastName": user.last_name,
        "zipcode": user.profile.zipcode,
    }


@pytest.fixture(params={**data.UpdateProfileForm.__members__})
def update_profile_params(request):
    return data.UpdateProfileForm[request.param].value


@pytest.fixture(params=factory.build_batch(dict, 5, FACTORY_CLASS=f.ProfileFactory))
def random_profile_dict(request):
    profile = request.param
    profile.pop("user")
    return request.param
