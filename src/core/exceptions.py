from typing import Optional

from rest_framework import exceptions
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import set_rollback


def custom_exception_handler(exc: APIException, context: dict) -> Optional[Response]:
    if isinstance(exc, exceptions.APIException):
        headers = get_headers(exc)
        data = get_data(exc)

        set_rollback()
        return Response(data, status=exc.status_code, headers=headers)


def get_headers(exc: APIException) -> dict:
    headers = {}
    if getattr(exc, "auth_header", None):
        headers["WWW-Authenticate"] = exc.auth_header
    if getattr(exc, "wait", None):
        headers["Retry-After"] = int(exc.wait)

    return headers


def get_data(exc: APIException) -> dict:
    if isinstance(exc.detail, (list, dict)):
        if "non_field_errors" in exc.detail:
            return {"error": ", ".join(exc.detail["non_field_errors"])}
        else:
            return exc.detail
    return {"error": exc.detail}
