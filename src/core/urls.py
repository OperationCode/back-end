from django.urls import include, path
from django.views.generic import TemplateView
from dj_rest_auth.registration.views import VerifyEmailView
from dj_rest_auth.views import PasswordChangeView, PasswordResetConfirmView
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from . import views


class DummyPasswordResetConfirmView(TemplateView):
    """
    Dummy view for URL generation only. The actual password reset confirm
    is handled by the PasswordResetConfirmView via POST.
    This pattern exists to satisfy Django's reverse() call in password reset emails.
    """
    template_name = ""


urlpatterns = [
    # URL pattern for email generation (reverse() compatibility)
    path(
        "auth/password/reset/confirm/<str:uidb64>/<str:token>/",
        DummyPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    # Actual API endpoint for password reset confirmation
    path(
        "auth/password/reset/confirm/",
        PasswordResetConfirmView.as_view(),
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
