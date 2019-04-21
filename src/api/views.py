import json
import logging

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User as AuthUser
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainSlidingView

from api.models import (
    CodeSchool,
    Location,
    Resource,
    Scholarship,
    ScholarshipApplication,
    TeamMember,
    UserInfo,
)
from api.serializers import (
    CodeSchoolSerializer,
    LocationSerializer,
    ResourceSerializer,
    ScholarshipSerializer,
    ScholarshipApplicationSerializer,
    TeamMemberSerializer,
    CustomTokenObtainSerializer,
    UserInfoSerializer,
)
from api.utils import error_response
from backend.tasks import send_slack_invite_job

logger = logging.getLogger(__name__)


class CustomTokenObtainView(TokenObtainSlidingView):
    """
    View for responding to JWT requests.

    Overrides the default error messaging
    """

    serializer_class = CustomTokenObtainSerializer

    def post(self, *args, **kwargs):
        try:
            return super().post(*args, **kwargs)

        except AuthenticationFailed as e:
            return error_response(
                "The email or password you entered is incorrect!", status=401
            )

        except Exception:
            return error_response(
                "Something is wrong on our end. Please try again later."
            )


@transaction.atomic
@csrf_exempt
def create_user(request):
    if request.method != "POST":
        return error_response("not found", status=404)

    body = json.loads(request.body)
    try:
        email = body["email"]
        password = body["password"]
        first_name = body["first_name"]
        last_name = body["last_name"]
        zipcode = body["zip"]

        if AuthUser.objects.filter(username=email).exists():
            return error_response("Account with email already exists")

        hashed_password = make_password(password)
        AuthUser.objects.create(
            username=email,
            email=email,
            password=hashed_password,
            first_name=first_name,
            last_name=last_name,
        )
        user_info = UserInfo.objects.get(user__username=email)
        user_info.zip = zipcode
        user_info.save()

        send_slack_invite_job(email)
        token = CustomTokenObtainSerializer.get_token(user_info.user)

        return JsonResponse({"token": str(token)})

    except KeyError as e:
        return error_response(f"Missing required field {e}")

    except Exception as e:
        logger.exception("Exception while created new user", e)
        return error_response("Unknown error occurred")


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


class UserInfoViewSet(ModelViewSet):
    serializer_class = UserInfoSerializer
    queryset = UserInfo.objects.all()
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class TestView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        # send_slack_invite_job("manthrian@gmail.com")
        content = {"message": "Started task!"}
        return Response(content)
