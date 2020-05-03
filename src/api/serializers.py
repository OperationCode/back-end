from rest_framework import serializers

from api.models import (
    CodeSchool,
    Location,
    Scholarship,
    ScholarshipApplication,
    SuccessStory,
    TeamMember,
)


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"


class CodeSchoolSerializer(serializers.ModelSerializer):
    locations = LocationSerializer(many=True, read_only=True)

    class Meta:
        model = CodeSchool
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


class SuccessStorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SuccessStory
        fields = "__all__"
