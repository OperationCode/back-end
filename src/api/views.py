from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

from api.models import (
    CodeSchool,
    Location,
    Scholarship,
    ScholarshipApplication,
    SuccessStory,
    TeamMember,
)
from api.serializers import (
    CodeSchoolSerializer,
    LocationSerializer,
    ScholarshipApplicationSerializer,
    ScholarshipSerializer,
    SuccessStorySerializer,
    TeamMemberSerializer,
)


class CodeSchoolViewSet(ReadOnlyModelViewSet):
    serializer_class = CodeSchoolSerializer
    queryset = CodeSchool.objects.all()


class LocationViewSet(ReadOnlyModelViewSet):
    serializer_class = LocationSerializer
    queryset = Location.objects.all()


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


class SuccessStoryViewSet(ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = SuccessStorySerializer
    queryset = SuccessStory.objects.all()
