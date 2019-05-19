from rest_framework import serializers

from api.models import (
    CodeSchool,
    Event,
    GitHubStatistic,
    GitHubUser,
    Location,
    Request,
    Resource,
    Scholarship,
    ScholarshipApplication,
    Service,
    Tag,
    TeamMember,
    Vote,
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


class EventSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"


class GitHubStatisticSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GitHubStatistic
        fields = "__all__"


class GitHubUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GitHubUser
        fields = "__all__"


class RequestSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Request
        fields = "__all__"


class ServiceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Service
        fields = "__all__"


class TagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class VoteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Vote
        fields = "__all__"
