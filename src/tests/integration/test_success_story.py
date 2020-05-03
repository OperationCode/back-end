import pytest
from django.db import models

from api.models import SuccessStory


@pytest.mark.django_db
def test_success_save():
    test_obj = SuccessStory(
        created_by="Bob Vila",
        created_at=models.DateTimeField(auto_now_add=True),
        text="This is some test text",
        is_approved=True,
    )
    test_obj.save()
    assert test_obj.created_by == "Bob Vila"
    assert test_obj.created_at
    assert test_obj.text == "This is some test text"
    assert test_obj.is_approved
