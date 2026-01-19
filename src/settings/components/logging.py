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


def traces_sampler(sampling_context):
    """
    Custom sampler to control which transactions are traced.
    Returns a sample rate between 0.0 and 1.0.

    Respects parent sampling decisions for distributed tracing.
    """
    # Respect parent sampling decision for distributed tracing
    parent_sampled = sampling_context.get("parent_sampled")
    if parent_sampled is not None:
        return float(parent_sampled)

    # Get transaction context
    transaction_context = sampling_context.get("transaction_context", {})
    transaction_name = transaction_context.get("name", "")

    # Also check WSGI environ for direct path access
    wsgi_environ = sampling_context.get("wsgi_environ", {})
    request_path = wsgi_environ.get("PATH_INFO", "")

    # Sample health check endpoints at 1% (to catch errors but reduce noise)
    if request_path in ["/healthz", "/health", "/readiness", "/liveness"]:
        return 0.01
    if any(health in transaction_name for health in ["/healthz", "/health", "/readiness", "/liveness"]):
        return 0.01

    # Use the configured sample rate for everything else
    return config("SENTRY_TRACES_SAMPLE_RATE", default=1.0, cast=float)


def before_send_transaction(event, hint):  # noqa: ARG001
    """
    Filter transactions before sending to Sentry.
    Returns None to drop the transaction, or the event to send it.

    Args:
        event: The transaction event
        hint: Additional context (unused but required by Sentry signature)
    """
    # Drop 404 transactions (not found errors are noise, not actionable issues)
    if event.get("contexts", {}).get("response", {}).get("status_code") == 404:
        return None

    return event

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
        # Performance Monitoring (Tracing) - use custom sampler to filter health checks
        traces_sampler=traces_sampler,
        # Filter transactions before sending (e.g., drop 404s)
        before_send_transaction=before_send_transaction,
        # Set profiles_sample_rate to 1.0 to profile 100% of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=config("SENTRY_PROFILES_SAMPLE_RATE", default=1.0, cast=float),
        # Send default PII like user IP and user ID to Sentry
        send_default_pii=config("SENTRY_SEND_DEFAULT_PII", default=True, cast=strtobool),
    )
