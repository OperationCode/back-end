from django.contrib.auth import get_user_model
from rest_auth.registration.serializers import (
    RegisterSerializer as BaseRegisterSerializer,
)
from rest_auth.registration.serializers import (
    SocialLoginSerializer as BaseSocialLoginSerializer,
)
from rest_auth.serializers import LoginSerializer as BaseLoginSerializer
from rest_auth.serializers import (
    PasswordResetConfirmSerializer as BasePasswordResetConfirmSerializer,
)
from rest_auth.serializers import UserDetailsSerializer as BaseUserDetailsSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.models import Profile


# noinspection PyAbstractClass
class LoginSerializer(BaseLoginSerializer):
    """
    Extends the default LoginSerializer in order to return
    custom error messages
    """

    def validate(self, attrs):
        try:
            return super().validate(attrs)
        except serializers.ValidationError as ex:
            ex.detail = "The email or password you entered is incorrect!"
            raise ex


# noinspection PyAbstractClass
class PasswordResetConfirmSerializer(BasePasswordResetConfirmSerializer):
    """
    Extends the default PasswordResetConfirmSerializer in order to return
    custom error messages
    """

    def validate(self, attrs):
        try:
            return super().validate(attrs)
        except serializers.ValidationError as ex:
            if "new_password2" in ex.detail:
                ex.detail = ex.detail["new_password2"][0]
            else:
                ex.detail = "Could not reset password.  Reset token expired or invalid."
            raise ex


# noinspection PyAbstractClass
class CustomSocialLoginSerializer(BaseSocialLoginSerializer):
    """
    Extends default SocialLoginSerializer to add additional details to some
    failed login attempts
    """

    def validate(self, attrs):
        try:
            res = super().validate(attrs)
            return res
        except ValidationError as ex:
            if "User is already registered with this e-mail address." in ex.detail:
                ex.detail[0] = (
                    "User is already registered with this e-mail address. "
                    "Please login using the form above."
                )
            raise ex


# noinspection PyAbstractClass
class RegisterSerializer(BaseRegisterSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    # legacy compat
    zip = serializers.CharField(write_only=True, required=False)
    zipcode = serializers.CharField(write_only=True, required=False)

    # Overrides the default required password fields
    password1 = None
    password2 = None

    def get_cleaned_data(self):
        return {
            "username": self.validated_data.get("email", ""),
            "email": self.validated_data.get("email", ""),
            # allauth uses password1 internally for creation
            "password1": self.validated_data.get("password", ""),
            "first_name": self.validated_data.get("first_name", ""),
            "last_name": self.validated_data.get("last_name", ""),
            "zipcode": self.validated_data.get("zipcode", ""),
        }

    def validate(self, data):
        return data


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
        representation["zipcode"] = profile["zipcode"]
        representation["is_mentor"] = profile["is_mentor"]
        return representation


class UserSerializer(BaseUserDetailsSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = UserModel
        fields = ("username", "email", "first_name", "last_name", "profile")
        read_only_fields = ("email",)

    def to_representation(self, instance: UserModel) -> dict:
        """Move fields from Profile to user representation."""
        representation = super().to_representation(instance)
        profile = representation.pop("profile")
        profile.pop("user")

        for key, val in profile.items():
            representation[key] = val

        return representation
