# Build stage (production dependencies only)
FROM python:3.10-alpine AS builder

# Install system dependencies needed for building
RUN apk update && apk upgrade
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    postgresql-dev \
    python3-dev \
    zlib-dev \
    jpeg-dev

# Create virtual environment
RUN python -m venv /venv

# Install Poetry in the virtual environment
RUN /venv/bin/pip install poetry

# Copy Poetry configuration
COPY pyproject.toml poetry.lock ./

# Configure Poetry to use our virtual environment and install dependencies
ENV POETRY_VENV_IN_PROJECT=false
ENV VIRTUAL_ENV=/venv
RUN /venv/bin/poetry install --only=main --compile --no-interaction --no-cache

# Test builder stage (includes dev dependencies)
FROM builder AS test-builder
RUN /venv/bin/poetry install --compile --no-interaction --no-cache

# Test stage
FROM python:3.10-alpine AS test
RUN apk update && apk upgrade
RUN apk add --no-cache libpq libjpeg-turbo

ENV PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH" \
    DJANGO_ENV=testing \
    ENVIRONMENT=TEST

COPY --from=test-builder /venv /venv
WORKDIR /app
COPY src ./src
COPY .dev ./src/.dev
COPY pytest.ini ./
WORKDIR /app/src

CMD ["pytest", "-v"]

# Production stage
FROM python:3.10-alpine AS production
RUN apk update && apk upgrade
RUN rm -rf /var/cache/apk/*

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH" \
    DJANGO_ENV=production \
    DB_ENGINE=django.db.backends.postgresql

# Install runtime dependencies
RUN apk add --no-cache \
    libpq \
    libjpeg-turbo

# Copy virtual environment from builder stage
COPY --from=builder /venv /venv

# Create application directory
WORKDIR /app

# Copy application code
COPY src ./src
COPY .dev ./src/.dev

# Pre-compile all Python bytecode for faster startup
RUN python -m compileall -j 0 ./src/

# Create static directory
RUN mkdir -p /static

# Set working directory to source
WORKDIR /app/src

# Expose port
EXPOSE 8000

# Default command
CMD ["sh", "-c", "python manage.py process_tasks & gunicorn operationcode_backend.wsgi -c /app/src/gunicorn_config.py"]
