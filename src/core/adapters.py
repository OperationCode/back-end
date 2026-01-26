from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailConfirmation
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from rest_framework.request import Request

from core.serializers import RegisterSerializer


class AccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(
        self, request: Request, emailconfirmation: EmailConfirmation
    ) -> str:
        """
        Constructs the email confirmation (activation) url.
        """
        site = Site.objects.get(pk=settings.SITE_ID)
        return f"https://{site.domain}/confirm_email?key={emailconfirmation.key}"

    def get_reset_password_from_key_url(self, key: str) -> str:
        """
        Constructs the password reset url for the frontend.
        The key parameter is in the format 'uidb36-token'.
        """
        site = Site.objects.get(pk=settings.SITE_ID)
        return f"https://{site.domain}/password_reset/confirm?key={key}"

    def save_user(
        self,
        request: Request,
        user: User,
        form: RegisterSerializer,
        commit: bool = True,
    ) -> User:
        """
        Adds the provided zip code to the profile attached
        to the newly created user
        """
        super().save_user(request, user, form)
        user.profile.zipcode = form.cleaned_data["zipcode"]
        user.profile.save()
        return user
