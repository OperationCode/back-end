# syntax=docker/dockerfile:1

# ============================================================================
# Build stage: Install dependencies using Poetry
# ============================================================================
FROM python:3.12-slim AS builder

# Install build dependencies required for compiling Python packages
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    rm -f /etc/apt/apt.conf.d/docker-clean && \
    apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl

# Install Poetry
ENV POETRY_VERSION=2.3.0 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN --mount=type=cache,target=/root/.cache \
    curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

WORKDIR /app

# Copy dependency files first for better layer caching
COPY pyproject.toml poetry.lock ./

# Install dependencies into a virtual environment
# Using --mount=type=cache speeds up rebuilds significantly
RUN --mount=type=cache,target=$POETRY_CACHE_DIR \
    poetry install --only=main --no-interaction --no-ansi --no-root

# ============================================================================
# Development builder: Install all dependencies including dev tools
# ============================================================================
FROM builder AS builder-dev

# Install all dependencies including dev (debug_toolbar, pytest, etc.)
RUN --mount=type=cache,target=$POETRY_CACHE_DIR \
    poetry install --no-interaction --no-ansi --no-root

# ============================================================================
# Development stage: Full development environment with dev tools
# ============================================================================
FROM python:3.12-slim AS development

LABEL org.opencontainers.image.source="https://github.com/operationcode/back-end"
LABEL org.opencontainers.image.description="Operation Code Backend - Development"
LABEL org.opencontainers.image.licenses="MIT"

# Install runtime dependencies
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    rm -f /etc/apt/apt.conf.d/docker-clean && \
    apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && apt-get upgrade -y

# Create non-root user for security
RUN groupadd -r appuser && \
    useradd -r -g appuser -u 1000 -m -d /app appuser

# Set environment variables for Python optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    PATH="/app/.venv/bin:$PATH" \
    VIRTUAL_ENV=/app/.venv

WORKDIR /app

# Copy virtual environment with dev dependencies from builder-dev stage
COPY --from=builder-dev --chown=appuser:appuser /app/.venv /app/.venv

# Copy application code
COPY --chown=appuser:appuser ./src ./src

# Set working directory to src for running the application
WORKDIR /app/src

# Switch to non-root user
USER appuser

# Expose port for Django dev server
EXPOSE 8000

# Run Django development server (will be overridden by docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# ============================================================================
# Production/Runtime stage: Minimal production image (DEFAULT)
# ============================================================================
FROM python:3.12-slim AS runtime

LABEL org.opencontainers.image.source="https://github.com/operationcode/back-end"
LABEL org.opencontainers.image.description="Operation Code Backend - Django API"
LABEL org.opencontainers.image.licenses="MIT"

# Install only runtime dependencies (no build tools)
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    rm -f /etc/apt/apt.conf.d/docker-clean && \
    apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && apt-get upgrade -y

# Create non-root user for security
RUN groupadd -r appuser && \
    useradd -r -g appuser -u 1000 -m -d /app appuser

# Set environment variables for Python optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    PATH="/app/.venv/bin:$PATH" \
    VIRTUAL_ENV=/app/.venv \
    DJANGO_Q_WORKERS=1

WORKDIR /app

# Copy virtual environment from builder stage (production deps only)
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy application code
COPY --chown=appuser:appuser ./src ./src

# Pre-compile Python bytecode for faster startup
RUN python -m compileall -q ./src/

# Set working directory to src for running the application
WORKDIR /app/src

# Switch to non-root user
USER appuser

# Expose port for Gunicorn
EXPOSE 8000

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/healthz || exit 1

# Run background task processor and gunicorn
CMD ["sh", "-c", "python manage.py qcluster & gunicorn operationcode_backend.wsgi -c gunicorn_config.py"]
