import logging

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from settings.components import ENVIRONMENT, config


def strtobool(value):
    """Convert string to boolean."""
    if isinstance(value, bool):
        return value
    value_lower = str(value).lower()
    if value_lower in ("true", "1", "yes", "y", "on"):
        return True
    if value_lower in ("false", "0", "no", "n", "off", ""):
        return False
    raise ValueError(f"Cannot convert '{value}' to boolean")

# Sentry.io error tracking
# https://docs.sentry.io/platforms/python/django/
SENTRY_DSN = config("SENTRY_DSN", default="")
RELEASE = config("RELEASE", default="0.0.0")

if SENTRY_DSN:  # pragma: no cover
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            LoggingIntegration(
                level=logging.INFO,  # Capture info and above as breadcrumbs
                event_level=logging.ERROR,  # Send errors and above as events
            ),
        ],
        environment=ENVIRONMENT,
        release=RELEASE,
        # Performance Monitoring (Tracing)
        traces_sample_rate=config("SENTRY_TRACES_SAMPLE_RATE", default=1.0, cast=float),
        # Set profiles_sample_rate to 1.0 to profile 100% of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=config("SENTRY_PROFILES_SAMPLE_RATE", default=1.0, cast=float),
        # Send default PII like user IP and user ID to Sentry
        send_default_pii=config("SENTRY_SEND_DEFAULT_PII", default=True, cast=strtobool),
    )
