from django.urls import include, path
from django.views.generic import TemplateView
from rest_auth.registration.views import SocialAccountListView, VerifyEmailView
from rest_auth.views import PasswordResetConfirmView
from rest_framework_jwt.views import refresh_jwt_token, verify_jwt_token

from . import views

urlpatterns = [
    path(
        "auth/password/reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("auth/verify-email/", VerifyEmailView.as_view(), name="rest_verify_email"),
    path("auth/social/google/", views.GoogleLogin.as_view(), name="google_rest_login"),
    path(
        "auth/social/google/connect",
        views.GoogleConnect.as_view(),
        name="google_connect",
    ),
    path("auth/social/facebook/", views.FacebookLogin.as_view(), name="fb_rest_login"),
    path(
        "auth/social/facebook/connect",
        views.FacebookConnect.as_view(),
        name="facebook_connect",
    ),
    path("auth/social/github/", views.GithubLogin.as_view(), name="gh_rest_login"),
    path("auth/social/list", SocialAccountListView.as_view(), name="social_list"),
    path("auth/token/refresh", refresh_jwt_token, name="refresh_jwt"),
    path("auth/token/verify", verify_jwt_token, name="verify_jwt"),
    path("auth/registration/", views.RegisterView.as_view(), name="rest_register"),
    path("auth/profile", views.UpdateProfile.as_view(), name="legacy_update_profile"),
    path("auth/profile/", views.UpdateProfile.as_view(), name="update_profile"),
    path("auth/user", views.UserView.as_view(), name="legacy_view_user"),
    path("auth/user/", views.UserView.as_view(), name="view_user"),
    # Used by allauth to send the "verification email sent" response to client
    path(
        "auth/account-email-verification-sent",
        TemplateView.as_view(),
        name="account_email_verification_sent",
    ),
    path("auth/", include("rest_auth.urls")),
    path("", include('django_prometheus.urls')),
]
