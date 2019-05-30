from rest_framework.exceptions import (
    APIException,
    PermissionDenied,
    AuthenticationFailed,
)

from core.exceptions import custom_exception_handler

mock_detail = "test_detail"


def test_permission_denied_formatted_correctly():
    ex = PermissionDenied(mock_detail)
    response = custom_exception_handler(ex, {})

    assert response.status_code == 403
    assert response.data["error"] == PermissionDenied.default_detail


def test_auth_header_formatted_correctly(client):
    ex = AuthenticationFailed(mock_detail)
    setattr(ex, "auth_header", 'Bearer realm="api"')
    response = custom_exception_handler(ex, {})

    assert response.status_code == 401
    assert response["WWW-Authenticate"] == 'Bearer realm="api"'


def test_retry_header_formatted_correctly(client):
    ex = APIException(mock_detail)
    setattr(ex, "wait", "30")
    response = custom_exception_handler(ex, {})

    assert response.status_code == 500
    assert response["Retry-After"] == "30"


def test_unknown_type_returns_none(client):
    response = custom_exception_handler({}, {})
    assert response is None
