from rest_framework import status
from rest_framework.exceptions import PermissionDenied


class CustomValidationError(PermissionDenied):
    """
    Exception that is re-raised on login validation exceptions
    in order to define our own error message responses
    """

    default_status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "The email or password you entered is incorrect!"

    def __init__(self, detail=default_detail, status_code=default_status_code):
        self.detail = {"error": detail}
        self.status_code = status_code
