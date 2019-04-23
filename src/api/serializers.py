from rest_framework import serializers

from api.models import (
    CodeSchool,
    Location,
    Resource,
    Scholarship,
    ScholarshipApplication,
    TeamMember,
)


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
