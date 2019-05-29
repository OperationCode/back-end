import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from settings.components import ENVIRONMENT, config

# Sentry.io error tracking
# https://docs.sentry.io/platforms/python/django/
SENTRY_DSN = config("SENTRY_DSN", default="")
RELEASE = config("RELEASE", default="0.0.0")

if SENTRY_DSN:  # pragma: no cover
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        environment=ENVIRONMENT,
        release=RELEASE,
    )
