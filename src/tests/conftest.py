import os

os.environ["ENVIRONMENT"] = "TEST"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.testing")

import django  # noqa: F402

# noinspection PyUnresolvedReferences
from .fixtures import *  # noqa: F402, F403


def pytest_configure(config):
    django.setup()
