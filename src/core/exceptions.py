from typing import Optional

from django.http import Http404
from rest_framework import exceptions
from rest_framework.exceptions import APIException, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import set_rollback


def custom_exception_handler(exc: APIException, context: dict) -> Optional[Response]:
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    if isinstance(exc, exceptions.APIException):
        headers = {}
        if getattr(exc, "auth_header", None):
            headers["WWW-Authenticate"] = exc.auth_header
        if getattr(exc, "wait", None):
            headers["Retry-After"] = int(exc.wait)

        if isinstance(exc.detail, (list, dict)):
            if "non_field_errors" in exc.detail:
                data = {"error": ", ".join(exc.detail["non_field_errors"])}
            else:
                data = exc.detail
        else:
            data = {"error": exc.detail}

        set_rollback()
        return Response(data, status=exc.status_code, headers=headers)

    return None
