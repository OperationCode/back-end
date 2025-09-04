FROM python:3.9-alpine AS base

# Using seperate docker stage for building dependencies
FROM base AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_VIRTUALENVS_OPTIONS_ALWAYS_COPY=1 \
    POETRY_VIRTUALENVS_PATH="/opt/venv" \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    VIRTUAL_ENVIRONMENT_PATH="/opt/venv"

# Install tools for building dependencies
RUN apk update && \
    apk add --no-cache libffi-dev \
                       postgresql-dev \
                       gcc \
                       python3-dev \
                       musl-dev \
                       zlib-dev \
                       jpeg-dev

COPY poetry.lock pyproject.toml ./

RUN pip install poetry
RUN poetry install

# The `built-image` stage is the base for all remaining images
# Pulls all of the built dependencies from the builder stage
FROM base AS built-image

# copy installed deps from builder image
COPY --from=builder /opt/venv /opt/venv

# Add libpq and libjpeg which psycopg2 and pillow need at runtime
RUN apk add --no-cache libpq libjpeg-turbo

# Make sure we use the virtualenv
ENV PATH="/opt/venv/bin:$PATH"

# The `app` stage is used as the base for images that don't
# need the development dependencies
FROM built-image AS app

ENV DJANGO_ENV=production
ENV DB_ENGINE=django.db.backends.postgresql
RUN mkdir /static
COPY src /src
COPY .dev /src/.dev
WORKDIR /src


# `Shell` will build an image that, when run, drops you into a
# python shell with the application context loaded
# Note this stage name is capitalised, this is purely
# a convetion for stages which result in useful images. Think of it like
# hint that this is a public interface
FROM app AS shell
LABEL shell=true
CMD ["python", "manage.py", "shell"]


# The `Prod` stage creates an image that will run the application using a
# production webserver and the `environments/production.py` configuration
FROM app AS prod

EXPOSE 8000
CMD ["sh", "-c", "python manage.py process_tasks & gunicorn operationcode_backend.wsgi -c /src/gunicorn_config.py"]
