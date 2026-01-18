# syntax=docker/dockerfile:1

# =============================================================================
# Builder stage: compile dependencies
# =============================================================================
FROM python:3.12-alpine AS builder

# Install build dependencies for compiling Python packages
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    postgresql-dev \
    python3-dev \
    zlib-dev \
    jpeg-dev

# Install poetry system-wide (not in venv, so it won't be copied to production)
RUN pip install --no-cache-dir poetry

# Create clean venv with upgraded pip (--upgrade-deps handles CVE-2025-8869)
RUN python -m venv /venv --upgrade-deps

WORKDIR /build
COPY pyproject.toml poetry.lock ./

# Tell poetry to use our venv instead of creating its own
ENV VIRTUAL_ENV=/venv \
    PATH="/venv/bin:$PATH"

# Install production dependencies only
RUN poetry install --only=main --no-interaction --no-cache --compile

# =============================================================================
# Test builder: add dev dependencies
# =============================================================================
FROM builder AS test-builder

RUN poetry install --no-interaction --no-cache --compile

# =============================================================================
# Runtime base: minimal image shared by test and production
# =============================================================================
FROM python:3.12-alpine AS runtime-base

# Install only runtime dependencies (no build tools, no poetry)
# Upgrade system pip to fix CVE-2025-8869 (even though app uses venv pip)
RUN apk upgrade --no-cache && \
    apk add --no-cache libpq libjpeg-turbo && \
    pip install --no-cache-dir --upgrade pip

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/venv/bin:$PATH"

WORKDIR /app

# =============================================================================
# Test stage
# =============================================================================
FROM runtime-base AS test

COPY --from=test-builder /venv /venv
COPY src ./src
COPY .dev ./src/.dev
COPY pytest.ini ./

WORKDIR /app/src

ENV DJANGO_ENV=testing \
    ENVIRONMENT=TEST

CMD ["pytest", "-v"]

# =============================================================================
# Production stage
# =============================================================================
FROM runtime-base AS production

COPY --from=builder /venv /venv
COPY src ./src
COPY .dev ./src/.dev

# Pre-compile Python bytecode for faster cold starts
RUN python -m compileall -q ./src/

WORKDIR /app/src

ENV DJANGO_ENV=production \
    DB_ENGINE=django.db.backends.postgresql

EXPOSE 8000

# Run background task processor and gunicorn
CMD ["sh", "-c", "python manage.py qcluster & gunicorn operationcode_backend.wsgi -c /app/src/gunicorn_config.py"]
