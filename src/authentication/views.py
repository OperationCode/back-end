import json
import logging

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User as AuthUser
from django.db import transaction
from django.http import JsonResponse

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainSlidingView

from authentication.models import UserInfo
from authentication.serializers import CustomTokenObtainSerializer, UserInfoSerializer
from api.utils import error_response
from backend.tasks import send_slack_invite_job, add_user_to_mailing_list

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

        except Exception as e:
            logger.exception(e)
            return error_response(
                "Something is wrong on our end. Please try again later."
            )

class RegisterView(CreateAPIView):
    pass

@transaction.atomic
@csrf_exempt
def create_user(request):
    if request.method != "POST":
        return error_response("not found", status=404)

    body = json.loads(request.body)
    try:
        email = body["email"]
        password = body["password"]
        first_name = body["firstName"]
        last_name = body["lastName"]
        zipcode = body["zipcode"]

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
        add_user_to_mailing_list(email, first_name, last_name)

        token = CustomTokenObtainSerializer.get_token(user_info.user)

        return JsonResponse({"token": str(token)})

    except KeyError as e:
        return error_response(f"Missing required field {e}")

    except Exception as e:
        logger.exception("Exception while created new user", e)
        return error_response("Unknown error occurred")


@csrf_exempt
def email_already_exists(request, email):
    return JsonResponse(
        {"available": not AuthUser.objects.filter(username=email).exists()}
    )


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
