import os

import django  # noqa: F402

# noinspection PyUnresolvedReferences
from .fixtures import *  # noqa: F402, F403

os.environ["ENVIRONMENT"] = "TEST"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.testing")


def pytest_configure(config):
    django.setup()
