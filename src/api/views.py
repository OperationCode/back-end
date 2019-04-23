from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from api.models import (
    CodeSchool,
    Location,
    Resource,
    Scholarship,
    ScholarshipApplication,
    TeamMember,
)
from api.serializers import (
    CodeSchoolSerializer,
    LocationSerializer,
    ResourceSerializer,
    ScholarshipSerializer,
    ScholarshipApplicationSerializer,
    TeamMemberSerializer,
)


class CodeSchoolViewSet(ModelViewSet):
    serializer_class = CodeSchoolSerializer
    queryset = CodeSchool.objects.all()


class LocationViewSet(ModelViewSet):
    serializer_class = LocationSerializer
    queryset = Location.objects.all()


class ResourceViewSet(ModelViewSet):
    serializer_class = ResourceSerializer
    queryset = Resource.objects.all()


class ScholarshipViewSet(ModelViewSet):
    serializer_class = ScholarshipSerializer
    queryset = Scholarship.objects.all()


class ScholarshipApplicationViewSet(ModelViewSet):
    serializer_class = ScholarshipApplicationSerializer
    queryset = ScholarshipApplication.objects.all()


class TeamMemberViewSet(ModelViewSet):
    serializer_class = TeamMemberSerializer
    queryset = TeamMember.objects.all()
