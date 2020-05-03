import pytest
from api.models import SuccessStory
from django.db import models


@pytest.mark.django_db
def success_save_test():
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
    assert test_obj.is_approved == True
