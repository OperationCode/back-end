from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailConfirmation
from django.conf import settings
from django.contrib.sites.models import Site
from rest_framework.request import Request


class AccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(
        self, request: Request, emailconfirmation: EmailConfirmation
    ) -> str:
        """
        Constructs the email confirmation (activation) url.

        """
        site = Site.objects.get(pk=settings.SITE_ID)
        return f"https://{site.domain}/confirm_email?key={emailconfirmation.key}"
