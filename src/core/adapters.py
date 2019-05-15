from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailConfirmation
from django.conf import settings
from django.contrib.auth.models import User as AuthUser
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

    def save_user(
        self,
        request: Request,
        user: AuthUser,
        form: RegisterSerializer,
        commit: bool = True,
    ):
        """
        Adds the provided zip code to the profile attached
        to the newly created user
        """
        super().save_user(request, user, form)
        user.profile.zip = form.cleaned_data["zip"]  # noqa
        user.profile.save()  # noqa
        return user
