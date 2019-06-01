FROM python:3.7-alpine AS base

# Using seperate docker stage for building dependencies
FROM base as builder

ENV PIP_DISABLE_PIP_VERSION_CHECK on
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_NO_BINARY psycopg2

# Install tools for building dependencies
RUN apk update && \
    apk add --no-cache libffi-dev \
                       postgresql-dev \
                       gcc \
                       python3-dev \
                       musl-dev \
                       # Pillow dependencies
                       zlib-dev \
                       jpeg-dev

RUN python -m venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

COPY poetry.lock pyproject.toml ./

RUN pip install poetry && \
    poetry config settings.virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi


# The `built-image` stage is the base for all remaining images
# Pulls all of the built dependencies from the builder stage
FROM base as built-image
ENV PIP_DISABLE_PIP_VERSION_CHECK on
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_NO_BINARY psycopg2

# copy installed deps from builder image
COPY --from=builder /opt/venv /opt/venv
# Add libpq which psycopg2 needs at runtime
RUN apk add --no-cache libpq
# Make sure we use the virtualenv
ENV PATH="/opt/venv/bin:$PATH"

# The `app` stage is used as the base for images that don't
# need the development dependencies
FROM built-image as app

ENV DJANGO_ENV production
ENV DB_ENGINE django.db.backends.postgresql
RUN mkdir /static
COPY src /src
WORKDIR /src


# The `dev-base` stage is used as the base for images that require
# the development dependencies. The duplication of the COPY instruction
# avoids breaking the cache for that later when the poetry.lock changes
FROM built-image AS dev-base

ENV DJANGO_ENV development
COPY poetry.lock pyproject.toml ./
RUN pip install poetry \
    && poetry config settings.virtualenvs.create false \
    && poetry install --no-interaction --no-ansi
COPY . /


# `Shell` will build an image that, when run, drops you into a
# python shell with the application context loaded
# Note this stage name is capitalised, this is purely
# a convetion for stages which result in useful images. Think of it like
# hint that this is a public interface
FROM app AS Shell
LABEL shell=true
CMD python manage.py shell


# `Dev` runs the application using the development web server, and enables
# developer tools like the debugger and interactive expcetions
FROM dev-base AS Dev
LABEL dev=true
EXPOSE 8000
WORKDIR /src

CMD python manage.py collectstatic --no-input;\
    gunicorn operationcode_backend.wsgi -b 0.0.0.0:8000 -w 3 --access-logfile=- --error-logfile=- --capture-output --logger-class "operationcode_backend.custom_logging.CustomGunicornLogger"

# The `Staging` stage is the same configuration as prod, the only
# difference being it doesn't process background tasks
# The resulting image will run the application using a
# production webserver and configuration
FROM app As Staging
EXPOSE 8000
CMD python manage.py collectstatic --no-input;\
    gunicorn operationcode_backend.wsgi -b 0.0.0.0:8000 -w 3 --access-logfile=- --error-logfile=- --capture-output --logger-class "operationcode_backend.custom_logging.CustomGunicornLogger"

# The `Prod` stage is the default stage if the Dockerfile is run without
# a target stage set. The resulting image will run the application using a
# production webserver and configuration
FROM app As Prod

EXPOSE 8000
CMD python manage.py collectstatic --no-input;\
    python manage.py process_tasks &\
    gunicorn operationcode_backend.wsgi -b 0.0.0.0:8000 -w 3 --access-logfile=- --error-logfile=- --capture-output --logger-class "operationcode_backend.custom_logging.CustomGunicornLogger"
