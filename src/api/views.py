from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

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
from api.serializers import (
    CodeSchoolSerializer,
    EventSerializer,
    GitHubStatisticSerializer,
    GitHubUserSerializer,
    LocationSerializer,
    RequestSerializer,
    ResourceSerializer,
    ScholarshipApplicationSerializer,
    ScholarshipSerializer,
    ServiceSerializer,
    TagSerializer,
    TeamMemberSerializer,
    VoteSerializer,
)


class CodeSchoolViewSet(ReadOnlyModelViewSet):
    serializer_class = CodeSchoolSerializer
    queryset = CodeSchool.objects.all()


class LocationViewSet(ReadOnlyModelViewSet):
    serializer_class = LocationSerializer
    queryset = Location.objects.all()


class ResourceViewSet(ReadOnlyModelViewSet):
    serializer_class = ResourceSerializer
    queryset = Resource.objects.all()


class ScholarshipViewSet(ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = ScholarshipSerializer
    queryset = Scholarship.objects.all()


class ScholarshipApplicationViewSet(ReadOnlyModelViewSet):
    serializer_class = ScholarshipApplicationSerializer
    queryset = ScholarshipApplication.objects.all()


class TeamMemberViewSet(ReadOnlyModelViewSet):
    serializer_class = TeamMemberSerializer
    queryset = TeamMember.objects.all()


class EventViewSet(ReadOnlyModelViewSet):
    serializer_class = EventSerializer
    queryset = Event.objects.all()


class GitHubStatisticViewSet(ReadOnlyModelViewSet):
    serializer_class = GitHubStatisticSerializer
    queryset = GitHubStatistic.objects.all()


class GitHubUserViewSet(ReadOnlyModelViewSet):
    serializer_class = GitHubUserSerializer
    queryset = GitHubUser.objects.all()


class RequestViewSet(ReadOnlyModelViewSet):
    serializer_class = RequestSerializer
    queryset = Request.objects.all()


class ServiceViewSet(ReadOnlyModelViewSet):
    serializer_class = ServiceSerializer
    queryset = Service.objects.all()


class TagViewSet(ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class VoteViewSet(ReadOnlyModelViewSet):
    serializer_class = VoteSerializer
    queryset = Vote.objects.all()
