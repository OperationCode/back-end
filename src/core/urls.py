from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework_jwt.views import refresh_jwt_token, verify_jwt_token

urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    # Used by allauth to send the "verification email sent" response to client
    path(
        "account-email-verification-sent",
        TemplateView.as_view(),
        name="account_email_verification_sent",
    ),
    path("auth/", include("rest_auth.urls")),
    path("auth/token/refresh", refresh_jwt_token, name="refresh_jwt"),
    path("auth/token/verify", verify_jwt_token, name="verify_jwt"),
    path("auth/registration/", include("rest_auth.registration.urls")),
]
