from rest_auth.serializers import LoginSerializer
from rest_framework import serializers, status
from rest_framework.exceptions import PermissionDenied


class CustomValidationError(PermissionDenied):
    """
    Exception that is re-raised on login validation exceptions
    in order to define our own error message responses
    """

    default_status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "The email or password you entered is incorrect!"

    def __init__(self, detail=default_detail, status_code=default_status_code):
        self.detail = {"error": detail}
        self.status_code = status_code


# noinspection PyAbstractClass
class CustomLoginSerializer(LoginSerializer):
    """
    Wraps the default LoginSerializer in order to return
    custom error messages
    """

    def validate(self, attrs):
        try:
            return super().validate(attrs)
        except serializers.ValidationError as ex:
            if "E-mail" in ex.detail[0]:
                raise CustomValidationError("Email has not been verified")
            else:
                raise CustomValidationError()
