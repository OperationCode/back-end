import json
import logging
from typing import Tuple

import requests
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.template.loader import render_to_string
from django.views.generic import FormView, TemplateView

from .forms import CodeSchoolForm

logger = logging.getLogger(__name__)


class IndexView(TemplateView):
    template_name = "frontend/index.html"
    link = ""  # placeholder for unique link


class CodeschoolFormView(FormView):
    """
    Temporary form for requesting a new codeschool to be added.
    Will eventually be replaced by a form on the front-end
    """

    form_class = CodeSchoolForm
    template_name = "frontend/codeschool-form.html"
    success_url = f"https://github.com/{settings.GITHUB_REPO}/issues"

    def form_valid(self, form):
        form.save()
        handle_submission(form.cleaned_data)
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


def get_logo_and_users(logo: InMemoryUploadedFile) -> Tuple[str, str]:
    school_logo = logo.name.replace(" ", "_")
    if settings.DEBUG or settings.TESTING:
        users = "@AllenAnthes"
    else:  # pragma: no cover
        users = "@AllenAnthes @kylemh @wimo7083"

    logo_url = f"{settings.MEDIA_URL}logos/{school_logo}"
    return logo_url, users


def handle_submission(form: dict) -> None:
    repo_path = settings.GITHUB_REPO
    url = f"https://api.github.com/repos/{repo_path}/issues"
    headers = {"Authorization": f"Bearer {settings.GITHUB_JWT}"}

    logo_url, notify_users = get_logo_and_users(form["logo"])
    form["logo_url"] = logo_url
    form["notify_users"] = notify_users

    body = render_to_string("code_school_ajax_body.txt", context=form)

    params = {"title": f"New Code School Request: {form['name']}", "body": body}
    res = requests.post(url, headers=headers, data=json.dumps(params))
    logger.info(f"response from github API call {res}")


class SurveyView(TemplateView):
    template_name = "frontend/survey.html"
