from dj_rest_auth.registration.views import VerifyEmailView
from dj_rest_auth.views import PasswordChangeView
from dj_rest_auth.views import PasswordResetConfirmView as RestPasswordResetConfirmView
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from . import views

urlpatterns = [
    # Custom password reset confirm view that handles allauth's UID encoding
    path(
        "auth/password/reset/confirm/<uidb64>/<token>/",
        views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    # Success page after password reset
    path(
        "auth/password/reset/complete/",
        TemplateView.as_view(template_name="registration/password_reset_complete.html"),
        name="password_reset_complete",
    ),
    # REST API endpoint for programmatic password reset (mobile apps, etc.)
    path(
        "auth/password/reset/confirm/",
        RestPasswordResetConfirmView.as_view(),
        name="rest_password_reset_confirm",
    ),
    path(
        "auth/password/change/",
        PasswordChangeView.as_view(),
        name="rest_password_change",
    ),
    path("auth/verify-email/", VerifyEmailView.as_view(), name="rest_verify_email"),
    path("auth/token/refresh", TokenRefreshView.as_view(), name="refresh_jwt"),
    path("auth/token/verify", TokenVerifyView.as_view(), name="verify_jwt"),
    path("auth/registration/", views.RegisterView.as_view(), name="rest_register"),
    path("auth/profile/", views.UpdateProfile.as_view(), name="update_profile"),
    path(
        "auth/profile/admin/",
        views.AdminUpdateProfile.as_view(),
        name="admin_update_profile",
    ),
    path("auth/user/", views.UserView.as_view(), name="view_user"),
    # Used by allauth to send the "verification email sent" response to client
    path(
        "auth/account-email-verification-sent",
        TemplateView.as_view(),
        name="account_email_verification_sent",
    ),
    path("auth/", include("dj_rest_auth.urls")),
]
