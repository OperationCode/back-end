from rest_framework import serializers, status
from rest_framework.exceptions import PermissionDenied
from rest_auth.serializers import (
    LoginSerializer as BaseLoginSerializer,
    UserDetailsSerializer as BaseUserDetailsSerializer,
)
from rest_auth.registration.serializers import (
    RegisterSerializer as BaseRegisterSerializer,
)
from django.contrib.auth import get_user_model

from core.models import Profile


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
class LoginSerializer(BaseLoginSerializer):
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


# noinspection PyAbstractClass
class RegisterSerializer(BaseRegisterSerializer):
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    firstName = serializers.CharField(write_only=True)
    lastName = serializers.CharField(write_only=True)
    zip = serializers.CharField(write_only=True)

    def get_cleaned_data(self):
        return {
            "username": self.validated_data.get("email", ""),
            "email": self.validated_data.get("email", ""),
            "password1": self.validated_data.get("password1", ""),
            "first_name": self.validated_data.get("firstName", ""),
            "last_name": self.validated_data.get("lastName", ""),
            "zip": self.validated_data.get("zip", ""),
        }

    def save(self, request):
        return super().save(request)


UserModel = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"


class UserDetailsSerializer(BaseUserDetailsSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = UserModel
        fields = ("username", "email", "first_name", "last_name", "profile")
        read_only_fields = ("email",)

    def to_representation(self, instance: UserModel) -> dict:
        """Move fields from Profile to user representation."""
        representation = super().to_representation(instance)
        profile = representation.pop("profile")
        representation["zip"] = profile["zip"]
        representation["mentor"] = profile["mentor"]
        return representation
