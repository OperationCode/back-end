from allauth.account import app_settings as allauth_settings
from allauth.account.utils import url_str_to_user_pk
from dj_rest_auth.registration.views import RegisterView as BaseRegisterView
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.views import (
    PasswordResetConfirmView as DjangoPasswordResetConfirmView,
)
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from drf_yasg.openapi import IN_QUERY, TYPE_STRING, Parameter
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated

from core.models import Profile
from core.permissions import HasGroupPermission
from core.serializers import (
    ProfileSerializer,
    UserSerializer,
)

sensitive_param = method_decorator(
    sensitive_post_parameters("password"), name="dispatch"
)

email_param = Parameter(
    "email",
    IN_QUERY,
    "Email belonging to the Profile's User instance",
    required=True,
    type=TYPE_STRING,
)


class UpdateProfile(RetrieveUpdateAPIView):
    """
    API View for retrieving and updating the logged in user's profile info like
    military service details, current employment, etc
    """

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        """
        Overrides `get_object` to pull the user profile
        off the current authenticated user
        """
        obj = self.request.user.profile
        self.check_object_permissions(self.request, obj)
        return obj


class AdminUpdateProfile(RetrieveUpdateAPIView):
    """
    Read or update user profiles
    """

    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    permission_classes = (HasGroupPermission,)
    required_groups = {
        "GET": ["ProfileAdmin"],
        "PUT": ["ProfileAdmin"],
        "PATCH": ["ProfileAdmin"],
    }

    def get_object(self):
        email = self.request.query_params.get("email")
        if email:
            try:
                profile = Profile.objects.get(user__email=email)
            except Profile.DoesNotExist:
                raise NotFound

            self.check_permissions(self.request)
            return profile

        raise ValidationError({"error": "Missing email query param"})

    @swagger_auto_schema(manual_parameters=[email_param])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(manual_parameters=[email_param])
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(manual_parameters=[email_param])
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)


class UserView(RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        """
        Overrides `get_object` to pull the user
        off the current authenticated session
        """
        obj = self.request.user
        self.check_object_permissions(self.request, obj)
        return obj


@sensitive_param
class RegisterView(BaseRegisterView):
    pass


class PasswordResetConfirmView(DjangoPasswordResetConfirmView):
    """
    Custom password reset confirm view that handles allauth's UID encoding format.

    Allauth uses url_str_to_user_pk/user_pk_to_url_str which creates shorter UIDs
    (e.g., 'd') compared to Django's standard base64 encoding (e.g., 'MTM').
    This view decodes the allauth UID format and uses allauth's token generator
    to work with Django's password reset form.
    """

    template_name = "registration/password_reset_confirm.html"
    success_url = "/auth/password/reset/complete/"
    # Use allauth's token generator (EmailAwarePasswordResetTokenGenerator)
    token_generator = allauth_settings.PASSWORD_RESET_TOKEN_GENERATOR()

    def get_user(self, uidb64):
        """
        Override to use allauth's UID decoding instead of Django's base64 decoding.
        """
        try:
            # Use allauth's URL string to user PK conversion
            uid = url_str_to_user_pk(uidb64)
            user = get_user_model()._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            user = None
        return user
