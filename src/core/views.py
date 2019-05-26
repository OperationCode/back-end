from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from rest_auth.registration.views import RegisterView as BaseRegisterView
from rest_auth.registration.views import SocialConnectView, SocialLoginView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from core.models import Profile
from core.serializers import ProfileSerializer, UserSerializer

sensitive_param = method_decorator(
    sensitive_post_parameters("password"), name="dispatch"
)


class UpdateProfile(RetrieveUpdateAPIView):
    """
    API View for retrieving and updating user profile info like
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


class GoogleLogin(SocialLoginView):
    permission_classes = (AllowAny,)
    adapter_class = GoogleOAuth2Adapter


class GoogleConnect(SocialConnectView):
    adapter_class = GoogleOAuth2Adapter


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


class FacebookConnect(SocialConnectView):
    adapter_class = FacebookOAuth2Adapter


class GithubLogin(SocialLoginView):
    adapter_class = GitHubOAuth2Adapter
    callback_url = settings.GITHUB_AUTH_CALLBACK_URL
    client_class = OAuth2Client
