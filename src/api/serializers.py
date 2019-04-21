from django.contrib.auth.models import User as AuthUser
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainSlidingSerializer

from api.models import (
    CodeSchool,
    Location,
    Resource,
    Scholarship,
    ScholarshipApplication,
    TeamMember,
    UserInfo,
)


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
        token["email"] = user.username
        token["first_name"] = user.first_name
        token["last_name"] = user.last_name

        user_info = UserInfo.objects.get(user__username=user.username)
        token["zipcode"] = user_info.zip
        token["isMentor"] = user_info.mentor
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


class LocationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"


class CodeSchoolSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CodeSchool
        fields = "__all__"


class ResourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Resource
        fields = "__all__"


class ScholarshipSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Scholarship
        fields = "__all__"


class ScholarshipApplicationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ScholarshipApplication
        fields = "__all__"


class TeamMemberSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TeamMember
        fields = "__all__"
