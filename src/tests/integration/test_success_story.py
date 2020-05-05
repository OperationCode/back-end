import pytest
from django.db import models

from api.models import SuccessStory
from tests.factories import SuccessFactory


@pytest.mark.django_db
def test_stories(success_story):
    db = SuccessStory.objects.all()
    assert db.get(created_by=success_story.created_by)
    assert db.get(created_at=success_story.created_at)
    assert db.get(text=success_story.text)
    assert db.get(is_approved=success_story.is_approved)
