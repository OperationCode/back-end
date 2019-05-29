import os

import django  # noqa: F402

from .fixtures import *  # noqa: F402, F403

os.environ["ENVIRONMENT"] = "TEST"
os.environ.setdefault("DJANGO_ENV", "testing")
os.environ["DJANGO_SETTINGS_MODULE"] = "settings"


def pytest_configure(config):
    django.setup()
