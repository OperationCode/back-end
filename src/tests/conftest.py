import django  # noqa: F402

from .fixtures import *  # noqa: F402, F403


def pytest_configure(config):
    django.setup()
