FROM python:3.7-alpine AS base

# Using seperate docker stage for building dependencies
FROM base as builder

ENV PIP_DISABLE_PIP_VERSION_CHECK on
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_NO_BINARY psycopg2

# Install tools for building dependencies
RUN apk update && apk add --no-cache libffi-dev postgresql-dev gcc python3-dev musl-dev

RUN python -m venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

COPY poetry.lock pyproject.toml ./

RUN pip install poetry && \
    # configures poetry to use the virtualenv we already created
    poetry config settings.virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

# Create actual image to be deployed
FROM base as prod

# copy installed deps from builder image
COPY --from=builder /opt/venv /opt/venv

# Add libpq which psycopg2 needs at runtime
RUN apk add --no-cache libpq

# Make sure we use the virtualenv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /src
RUN mkdir /static
COPY src /src

EXPOSE 8000
CMD python manage.py collectstatic --no-input;python manage.py makemigrations;\
    python manage.py migrate;\
    gunicorn operationcode_backend.wsgi -b 0.0.0.0:8000 -w 3 --access-logfile=- --error-logfile=- --capture-output
