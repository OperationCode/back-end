from dj_rest_auth.registration.serializers import (
    RegisterSerializer as BaseRegisterSerializer,
)
from dj_rest_auth.serializers import LoginSerializer as BaseLoginSerializer
from dj_rest_auth.serializers import (
    PasswordResetConfirmSerializer as BasePasswordResetConfirmSerializer,
)
from dj_rest_auth.serializers import UserDetailsSerializer as BaseUserDetailsSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers

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
class RegisterSerializer(BaseRegisterSerializer):
    # Override username to not be required (we use email as username)
    username = serializers.CharField(required=False, allow_blank=True)
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
        # Set username to email if not provided
        if not data.get("username"):
            data["username"] = data.get("email", "")
        # Check for duplicate email - this prevents hitting DB unique constraint
        from django.contrib.auth import get_user_model

        User = get_user_model()
        if User.objects.filter(email=data.get("email")).exists():
            raise serializers.ValidationError(
                {"email": ["A user with that email already exists."]}
            )
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
        # Add camelCase aliases for backwards compatibility
        representation["firstName"] = representation.get("first_name", "")
        representation["lastName"] = representation.get("last_name", "")
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
