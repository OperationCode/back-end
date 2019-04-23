from django.contrib.auth.models import User as AuthUser
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainSlidingSerializer

from authentication.models import UserInfo


# noinspection PyAbstractClass
class CustomTokenObtainSerializer(TokenObtainSlidingSerializer):
    """
    Extends the Sliding Token serializer to include our custom claims
    to send to the frontend
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        user_info = UserInfo.objects.get(user__username=user.username)
        token["user"] = {
            "email": user.username,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "zipcode": user_info.zip,
            "isMentor": user_info.mentor,
        }

        return token


class AuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = (
            "id",
            "username",
            "email",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
        )


class UserInfoSerializer(serializers.ModelSerializer):
    user = AuthUserSerializer()

    class Meta:
        model = UserInfo
        fields = "__all__"

    def create(self, validated_data):
        user_data = {
            key: value for key, value in validated_data.pop("user").items() if value
        }
        user, created = AuthUser.objects.get_or_create(**user_data)
        userinfo = UserInfo.objects.create(**validated_data, user=user)

        return userinfo

    # def update(self, instance, validated_data):
    #     user_data = validated_data.pop('user')

class RegisterSerializer(serializers.Serializer):
