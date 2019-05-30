"""
This is a django-split-settings main file.
For more information read this:
https://github.com/sobolevn/django-split-settings
To change settings file:
`DJANGO_ENV=production python manage.py runserver`
"""
from os import environ

from split_settings.tools import include, optional

# Managing environment via DJANGO_ENV variable:
environ.setdefault("DJANGO_ENV", "development")
ENV = environ["DJANGO_ENV"]

# Include settings:
include(
    "components/*.py",
    # Select the right env:
    f"environments/{ENV}.py",
    # Optionally override some settings:
    optional("environments/local.py"),
)
