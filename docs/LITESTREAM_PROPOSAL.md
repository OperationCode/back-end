# Migration Guide: RDS PostgreSQL to SQLite + Litestream

This document outlines the migration from Amazon RDS PostgreSQL to SQLite with Litestream replication on S3, plus the compute migration from Spot instances to On-Demand with Savings Plans.

**Total Annual Savings: ~$197/year** while gaining reliable compute (no more spot interruptions) and 2× RAM.

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Phase 1: Infrastructure Setup](#phase-1-infrastructure-setup)
5. [Phase 2: Application Changes](#phase-2-application-changes)
6. [Phase 3: Migration Execution](#phase-3-migration-execution)
7. [Phase 4: Cutover](#phase-4-cutover)
8. [Phase 5: Cleanup](#phase-5-cleanup)
9. [Phase 6: Compute Migration (Spot → On-Demand + Savings Plan)](#phase-6-compute-migration-spot--on-demand--savings-plan)
10. [Rollback Plan](#rollback-plan)
11. [Monitoring & Troubleshooting](#monitoring--troubleshooting)
12. [Cost Comparison](#cost-comparison)

---

## Overview

### Current State
| Component | Value |
|-----------|-------|
| Database | RDS PostgreSQL 13.20 |
| Instance | db.t4g.micro |
| Configuration | Multi-AZ |
| Monthly Cost | ~$29 |
| Storage | 20 GB gp2 |

### Target State
| Component | Value |
|-----------|-------|
| Database | SQLite 3.x |
| Replication | Litestream → S3 |
| Recovery | Point-in-time (continuous) |
| DB Monthly Cost | ~$0.05 (S3 storage only) |
| Compute | 2× t4g.small On-Demand |
| Compute Monthly Cost | ~$17.50 (with Savings Plan) |
| Reliability | No spot interruptions |

### Why This Works for Operation Code
- **23 legitimate requests/day** - Single writer is sufficient
- **2 simple models** - No PostgreSQL-specific features
- **1 ECS replica** - No multi-writer concerns
- **Low data volume** - SQLite handles this easily

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     ECS Task                                 │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                   Container                          │    │
│  │  ┌─────────────┐     ┌──────────────────────────┐   │    │
│  │  │   Django    │────▶│  SQLite (/data/db.sqlite3) │   │    │
│  │  │   + Q2      │     └──────────────────────────┘   │    │
│  │  └─────────────┘              │                     │    │
│  │                               │                     │    │
│  │  ┌─────────────┐              │ watches             │    │
│  │  │ Litestream  │◀─────────────┘                     │    │
│  │  └──────┬──────┘                                    │    │
│  └─────────┼────────────────────────────────────────────┘    │
└────────────┼────────────────────────────────────────────────┘
             │ continuous replication
             ▼
      ┌──────────────┐
      │     S3       │
      │  (replicas)  │
      └──────────────┘
```

### Startup Flow
1. Container starts
2. Litestream restores latest SQLite from S3 (if exists)
3. Django starts with restored database
4. Litestream begins continuous replication to S3

### Failure Recovery
1. ECS detects unhealthy task
2. ECS terminates task, starts new one
3. New task restores from S3 (< 30 seconds for small DB)
4. Service continues with minimal downtime

---

## Prerequisites

- [ ] AWS CLI configured with appropriate permissions
- [ ] Terraform installed (for infrastructure changes)
- [ ] Access to `operationcode_infra` repository
- [ ] Access to AWS Secrets Manager
- [ ] Backup of current RDS database

---

## Phase 1: Infrastructure Setup

### 1.1 Create S3 Bucket for Litestream Replicas

Add to `operationcode_infra/terraform/storage.tf` (create if doesn't exist):

```hcl
# S3 bucket for Litestream SQLite replicas
resource "aws_s3_bucket" "litestream" {
  bucket = "operationcode-litestream-replicas"

  tags = {
    Name        = "Litestream SQLite Replicas"
    Environment = "production"
  }
}

resource "aws_s3_bucket_versioning" "litestream" {
  bucket = aws_s3_bucket.litestream.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "litestream" {
  bucket = aws_s3_bucket.litestream.id

  rule {
    id     = "cleanup-old-generations"
    status = "Enabled"

    # Keep only last 7 days of point-in-time recovery
    expiration {
      days = 7
    }

    noncurrent_version_expiration {
      noncurrent_days = 3
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "litestream" {
  bucket = aws_s3_bucket.litestream.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Block public access
resource "aws_s3_bucket_public_access_block" "litestream" {
  bucket = aws_s3_bucket.litestream.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
```

### 1.2 Create IAM Policy for Litestream S3 Access

Add to `operationcode_infra/terraform/iam.tf` (create if doesn't exist):

```hcl
# IAM policy for Litestream S3 access
resource "aws_iam_policy" "litestream_s3" {
  name        = "litestream-s3-access"
  description = "Allow Litestream to read/write SQLite replicas to S3"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.litestream.arn,
          "${aws_s3_bucket.litestream.arn}/*"
        ]
      }
    ]
  })
}

# Attach to ECS task execution role
resource "aws_iam_role_policy_attachment" "ecs_litestream_s3" {
  role       = data.aws_iam_role.ecs_task_execution_role.name
  policy_arn = aws_iam_policy.litestream_s3.arn
}
```

### 1.3 Apply Terraform Changes

```bash
cd /Users/irving/src/operationcode/operationcode_infra/terraform
terraform plan -out=litestream.plan
terraform apply litestream.plan
```

---

## Phase 2: Application Changes

### 2.1 Create Litestream Configuration

Create `src/litestream.yml`:

```yaml
# Litestream configuration for SQLite replication to S3
dbs:
  - path: /data/db.sqlite3
    replicas:
      - type: s3
        bucket: operationcode-litestream-replicas
        path: python-backend/prod
        region: us-east-2
        # Sync every 1 second (near real-time)
        sync-interval: 1s
        # Snapshot every hour for faster recovery
        snapshot-interval: 1h
        # Validation settings
        validation-interval: 5m
```

### 2.2 Create Startup Script

Create `src/docker-entrypoint.sh`:

```bash
#!/bin/sh
set -e

DB_PATH="/data/db.sqlite3"
LITESTREAM_CONFIG="/app/src/litestream.yml"

# Function to run Django
run_django() {
    echo "Starting Django application..."
    cd /app/src

    # Run migrations
    python manage.py migrate --noinput

    # Start Q cluster in background and Gunicorn in foreground
    python manage.py qcluster &
    exec gunicorn operationcode_backend.wsgi -c /app/src/gunicorn_config.py
}

# If LITESTREAM_ENABLED is not set or false, just run Django directly
if [ "${LITESTREAM_ENABLED}" != "true" ]; then
    echo "Litestream disabled, running Django directly..."
    run_django
    exit 0
fi

echo "Litestream enabled, setting up replication..."

# Ensure data directory exists
mkdir -p /data

# Restore database from S3 if it exists
echo "Attempting to restore database from S3..."
if litestream restore -if-replica-exists -config "$LITESTREAM_CONFIG" "$DB_PATH"; then
    echo "Database restored from S3 replica"
else
    echo "No existing replica found, starting fresh"
fi

# Start Litestream with Django as subprocess
# Litestream will replicate the database and manage the Django process
exec litestream replicate -exec "sh -c 'cd /app/src && python manage.py migrate --noinput && python manage.py qcluster & gunicorn operationcode_backend.wsgi -c /app/src/gunicorn_config.py'" -config "$LITESTREAM_CONFIG"
```

Make it executable:
```bash
chmod +x src/docker-entrypoint.sh
```

### 2.3 Update Dockerfile

Replace the production stage in `Dockerfile`:

```dockerfile
# =============================================================================
# Production stage
# =============================================================================
FROM runtime-base AS production

# Install Litestream
ARG LITESTREAM_VERSION=0.3.13
RUN wget -O /tmp/litestream.tar.gz \
    "https://github.com/benbjohnson/litestream/releases/download/v${LITESTREAM_VERSION}/litestream-v${LITESTREAM_VERSION}-linux-amd64.tar.gz" && \
    tar -xzf /tmp/litestream.tar.gz -C /usr/local/bin && \
    rm /tmp/litestream.tar.gz && \
    chmod +x /usr/local/bin/litestream

COPY --from=builder /venv /venv
COPY src ./src
COPY .dev ./src/.dev

# Pre-compile Python bytecode for faster cold starts
RUN python -m compileall -q ./src/

# Create data directory for SQLite
RUN mkdir -p /data && chmod 755 /data

WORKDIR /app/src

ENV DJANGO_ENV=production \
    PYTHONUNBUFFERED=1

EXPOSE 8000

# Use entrypoint script for Litestream integration
COPY src/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
```

### 2.4 Update Django Settings

Update `src/settings/environments/production.py`:

```python
import os

from settings.components import config
from settings.components.base import DATABASES, MIDDLEWARE

ALLOWED_HOSTS = ["api.operationcode.org"]
DEBUG = False

# Required for Django 4.0+ CSRF protection with HTTPS
CSRF_TRUSTED_ORIGINS = ["https://api.operationcode.org"]

if config("EXTRA_HOSTS", default=""):
    ALLOWED_HOSTS += [s.strip() for s in os.environ["EXTRA_HOSTS"].split(",")]

# Needed for AWS health check
if "allow_cidr.middleware.AllowCIDRMiddleware" not in MIDDLEWARE:
    MIDDLEWARE += ("allow_cidr.middleware.AllowCIDRMiddleware",)
ALLOWED_CIDR_NETS = ["192.168.0.0/16", "10.0.0.0/8", "172.16.0.0/12", "100.64.0.0/10"]

# Database configuration - supports both PostgreSQL and SQLite
DB_ENGINE = config("DB_ENGINE", default="django.db.backends.sqlite3")

if DB_ENGINE == "django.db.backends.sqlite3":
    # SQLite configuration for Litestream
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": config("DB_NAME", default="/data/db.sqlite3"),
            # SQLite optimizations for production
            "OPTIONS": {
                "timeout": 20,  # Wait up to 20 seconds for locks
                "init_command": (
                    "PRAGMA journal_mode=WAL;"  # Required for Litestream
                    "PRAGMA synchronous=NORMAL;"  # Good balance of safety/speed
                    "PRAGMA busy_timeout=5000;"  # 5 second busy timeout
                    "PRAGMA cache_size=-64000;"  # 64MB cache
                    "PRAGMA foreign_keys=ON;"  # Enforce FK constraints
                ),
            },
        }
    }

    # Django-Q2: Use synchronous mode for SQLite (simpler, works well for low volume)
    Q_CLUSTER = {
        "name": "operationcode",
        "workers": 1,  # Single worker for SQLite
        "timeout": 60,
        "retry": 120,
        "queue_limit": 50,
        "bulk": 10,
        "orm": "default",
        "sync": False,  # Still async, but single worker
    }
else:
    # PostgreSQL configuration (legacy, for rollback)
    DATABASES = {
        "default": {
            **DATABASES["default"],
            "ENGINE": DB_ENGINE,
        }
    }

# Honeycomb beeline auto-instrumentation
if "beeline.middleware.django.HoneyMiddleware" not in MIDDLEWARE:
    MIDDLEWARE += ("beeline.middleware.django.HoneyMiddleware",)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = config("BUCKET_REGION_NAME")  # e.g. us-east-2
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
AWS_DEFAULT_ACL = None
AWS_LOCATION = "static"
STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/"
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"
STATICFILES_LOCATION = "static"
MEDIAFILES_LOCATION = "media"
STATICFILES_STORAGE = "custom_storages.StaticStorage"
DEFAULT_FILE_STORAGE = "custom_storages.MediaStorage"

EMAIL_BACKEND = "anymail.backends.mandrill.EmailBackend"
```

### 2.5 Update Terraform Task Definition

Update `operationcode_infra/terraform/python_backend/main.tf`:

```hcl
locals {
  long_env_name = var.env == "prod" ? "production" : var.env

  # Resources (unchanged)
  cpu    = var.env == "prod" ? 256 : 256
  memory = var.env == "prod" ? 512 : 384
  count  = var.env == "prod" ? 1 : 1

  secrets     = jsondecode(data.aws_secretsmanager_secret_version.ecs-secrets.secret_string)
  secrets_env = nonsensitive(toset([for i, v in local.secrets : tomap({ "name" = upper(i), "valueFrom" = "${data.aws_secretsmanager_secret.ecs.arn}:${i}::" })]))

  # Litestream settings
  use_litestream = var.env == "prod" ? true : false
  db_engine      = local.use_litestream ? "django.db.backends.sqlite3" : "django.db.backends.postgresql"
}

resource "aws_ecs_task_definition" "python_backend" {
  family             = "python_backend_${var.env}"
  execution_role_arn = var.task_execution_role
  task_role_arn      = var.task_execution_role  # Needed for S3 access
  network_mode       = "bridge"
  cpu                = local.cpu
  memory             = local.memory

  container_definitions = jsonencode([
    {
      name      = "python_backend_${var.env}"
      image     = "633607774026.dkr.ecr.us-east-2.amazonaws.com/back-end:${var.image_tag}"
      essential = true

      portMappings = [
        {
          containerPort = 8000
          hostPort      = 0
          protocol      = "tcp"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = var.logs_group
          awslogs-region        = "us-east-2"
          awslogs-stream-prefix = "python_backend_${var.env}"
        }
      }

      healthCheck = {
        command     = ["CMD-SHELL", "wget -q -O /dev/null http://localhost:8000/healthz"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }

      environment = [
        {
          "name" : "ENVIRONMENT",
          "value" : "aws_ecs_${var.env}"
        },
        {
          "name" : "EXTRA_HOSTS",
          "value" : "*"
        },
        {
          "name" : "RELEASE",
          "value" : "1.0.2"  # Bump version
        },
        {
          "name" : "SITE_ID",
          "value" : "4"
        },
        {
          "name" : "DJANGO_ENV",
          "value" : "${local.long_env_name}"
        },
        {
          "name" : "GITHUB_REPO",
          "value" : "operationcode/back-end"
        },
        {
          "name" : "HONEYCOMB_DATASET",
          "value" : "${local.long_env_name}-traces"
        },
        {
          "name" : "DB_ENGINE",
          "value" : local.db_engine
        },
        {
          "name" : "DB_NAME",
          "value" : "/data/db.sqlite3"
        },
        {
          "name" : "LITESTREAM_ENABLED",
          "value" : tostring(local.use_litestream)
        },
        {
          "name" : "TZ",
          "value" : "UTC"
        },
      ]

      secrets = local.secrets_env

      mountPoints = []
      volumesFrom = []
  }])
}

# ... rest of file unchanged ...
```

---

## Phase 3: Migration Execution

### 3.1 Create Migration Script

Create `scripts/migrate_pg_to_sqlite.sh`:

```bash
#!/bin/bash
set -e

# Configuration
RDS_HOST="${DB_HOST}"
RDS_PORT="${DB_PORT:-5432}"
RDS_USER="${DB_USER}"
RDS_PASSWORD="${DB_PASSWORD}"
RDS_DATABASE="${DB_NAME}"
SQLITE_PATH="${1:-/tmp/db.sqlite3}"
S3_BUCKET="operationcode-litestream-replicas"
S3_PATH="python-backend/prod"

echo "=== PostgreSQL to SQLite Migration ==="
echo "Source: ${RDS_HOST}:${RDS_PORT}/${RDS_DATABASE}"
echo "Target: ${SQLITE_PATH}"
echo ""

# Step 1: Export data from PostgreSQL using Django
echo "Step 1: Exporting data from PostgreSQL..."
export DB_ENGINE=django.db.backends.postgresql
export DJANGO_ENV=production

cd /app/src

# Dump data using Django's dumpdata (preserves relationships)
python manage.py dumpdata \
    --natural-foreign \
    --natural-primary \
    --exclude contenttypes \
    --exclude auth.permission \
    --exclude admin.logentry \
    --exclude sessions \
    --indent 2 \
    > /tmp/data_dump.json

echo "Data exported to /tmp/data_dump.json"

# Step 2: Create fresh SQLite database
echo ""
echo "Step 2: Creating SQLite database..."
rm -f "${SQLITE_PATH}"
export DB_ENGINE=django.db.backends.sqlite3
export DB_NAME="${SQLITE_PATH}"

# Run migrations to create schema
python manage.py migrate --noinput

echo "SQLite schema created"

# Step 3: Load data into SQLite
echo ""
echo "Step 3: Loading data into SQLite..."
python manage.py loaddata /tmp/data_dump.json

echo "Data loaded successfully"

# Step 4: Verify data
echo ""
echo "Step 4: Verifying data..."
python manage.py shell -c "
from django.contrib.auth.models import User
from core.models import Profile

user_count = User.objects.count()
profile_count = Profile.objects.count()

print(f'Users: {user_count}')
print(f'Profiles: {profile_count}')

if user_count == 0:
    print('WARNING: No users found!')
    exit(1)
print('Verification passed!')
"

# Step 5: Upload to S3 for Litestream
echo ""
echo "Step 5: Uploading initial database to S3..."

# Initialize Litestream replica
litestream replicate -config /app/src/litestream.yml &
LITESTREAM_PID=$!
sleep 5  # Let Litestream create initial snapshot
kill $LITESTREAM_PID 2>/dev/null || true

echo ""
echo "=== Migration Complete ==="
echo "SQLite database: ${SQLITE_PATH}"
echo "S3 replica: s3://${S3_BUCKET}/${S3_PATH}"
echo ""
echo "Next steps:"
echo "1. Verify the data in SQLite"
echo "2. Update ECS task definition to use SQLite"
echo "3. Deploy new container"
echo "4. Monitor for issues"
echo "5. Delete RDS instance after validation period"
```

### 3.2 Run Migration

Option A: Run locally (recommended for testing):

```bash
# Pull production secrets
aws secretsmanager get-secret-value \
    --secret-id prod/python_backend \
    --query SecretString --output text | jq -r 'to_entries[] | "export \(.key | ascii_upcase)=\(.value)"' > /tmp/env.sh
source /tmp/env.sh

# Run migration
docker build -t backend-migrate --target production .
docker run --rm \
    -e DB_HOST -e DB_PORT -e DB_USER -e DB_PASSWORD -e DB_NAME \
    -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY \
    -v /tmp/migration:/data \
    backend-migrate \
    /bin/sh /app/scripts/migrate_pg_to_sqlite.sh /data/db.sqlite3
```

Option B: Run as ECS one-off task:

```bash
# Create migration task definition and run it
aws ecs run-task \
    --cluster operationcode-ecs-us-east-2 \
    --task-definition python_backend_migration \
    --count 1
```

---

## Phase 4: Cutover

### 4.1 Pre-Cutover Checklist

- [ ] Migration script completed successfully
- [ ] SQLite database verified with correct data
- [ ] Litestream replica exists in S3
- [ ] New Docker image built and pushed to ECR
- [ ] Terraform changes applied
- [ ] Maintenance window scheduled (if needed)

### 4.2 Cutover Steps

```bash
# 1. Build and push new Docker image
cd /Users/irving/src/operationcode/back-end
docker build -t backend:litestream --target production .
docker tag backend:litestream 633607774026.dkr.ecr.us-east-2.amazonaws.com/back-end:latest
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 633607774026.dkr.ecr.us-east-2.amazonaws.com
docker push 633607774026.dkr.ecr.us-east-2.amazonaws.com/back-end:latest

# 2. Apply Terraform changes
cd /Users/irving/src/operationcode/operationcode_infra/terraform
terraform apply

# 3. Force new deployment
aws ecs update-service \
    --cluster operationcode-ecs-us-east-2 \
    --service python_backend_prod \
    --force-new-deployment

# 4. Watch deployment
aws ecs wait services-stable \
    --cluster operationcode-ecs-us-east-2 \
    --services python_backend_prod

echo "Deployment complete!"
```

### 4.3 Post-Cutover Verification

```bash
# Check service health
curl -s https://api.operationcode.org/healthz

# Check logs for errors
aws logs tail /ecs/python_backend_prod --since 10m --follow

# Verify Litestream is replicating
aws s3 ls s3://operationcode-litestream-replicas/python-backend/prod/ --recursive | head -20
```

---

## Phase 5: Cleanup

### 5.1 Validation Period

Wait **7 days** before deleting RDS to ensure:
- No data issues discovered
- Application performs correctly
- Litestream recovery works as expected

### 5.2 Delete RDS Instance

```bash
# Create final snapshot before deletion
aws rds create-db-snapshot \
    --db-instance-identifier python-prod \
    --db-snapshot-identifier python-prod-final-backup-$(date +%Y%m%d)

# Delete RDS instance (keep final snapshot)
aws rds delete-db-instance \
    --db-instance-identifier python-prod \
    --skip-final-snapshot \
    --delete-automated-backups
```

### 5.3 Update Secrets Manager

Remove database credentials from Secrets Manager (no longer needed):
- `DB_HOST`
- `DB_PORT`
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME` (keep if using for SQLite path)

---

## Rollback Plan

### Immediate Rollback (< 5 minutes)

If issues occur immediately after cutover:

```bash
# 1. Revert environment variables in Terraform
# Set use_litestream = false in main.tf

# 2. Apply Terraform
cd /Users/irving/src/operationcode/operationcode_infra/terraform
terraform apply

# 3. Force new deployment
aws ecs update-service \
    --cluster operationcode-ecs-us-east-2 \
    --service python_backend_prod \
    --force-new-deployment
```

### Rollback After Data Changes

If rollback needed after new data has been written to SQLite:

```bash
# 1. Export data from SQLite
docker exec -it <container_id> python manage.py dumpdata \
    --natural-foreign \
    --natural-primary \
    --exclude contenttypes \
    --exclude auth.permission \
    > /tmp/sqlite_data.json

# 2. Switch back to PostgreSQL (via Terraform)

# 3. Load new data into PostgreSQL
docker exec -it <container_id> python manage.py loaddata /tmp/sqlite_data.json
```

---

## Monitoring & Troubleshooting

### CloudWatch Metrics to Monitor

- ECS Task CPU/Memory utilization
- ALB Target response time
- ALB 5xx error count
- S3 PUT requests to litestream bucket

### Common Issues

#### Issue: "database is locked" errors

**Cause**: Multiple processes trying to write simultaneously

**Solution**: Ensure only one worker in Q_CLUSTER:
```python
Q_CLUSTER = {
    "workers": 1,
    ...
}
```

#### Issue: Slow startup time

**Cause**: Large database taking time to restore from S3

**Solution**: Increase `startPeriod` in health check:
```hcl
healthCheck = {
    startPeriod = 120  # Increase from 60
    ...
}
```

#### Issue: Data not persisting after restart

**Cause**: Litestream not replicating properly

**Solution**: Check Litestream logs:
```bash
aws logs filter-log-events \
    --log-group-name /ecs/python_backend_prod \
    --filter-pattern "litestream"
```

### Litestream Health Check

Add to your application's `/healthz` endpoint:

```python
# In your health check view
import os
import time

def healthz(request):
    checks = {"status": "ok"}

    # Check SQLite is accessible
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = str(e)
        checks["status"] = "error"

    # Check Litestream replica freshness (optional)
    if os.environ.get("LITESTREAM_ENABLED") == "true":
        db_path = "/data/db.sqlite3"
        if os.path.exists(db_path):
            age = time.time() - os.path.getmtime(db_path)
            checks["db_age_seconds"] = age
            if age > 300:  # 5 minutes
                checks["warning"] = "Database not modified recently"

    return JsonResponse(checks)
```

---

## Cost Comparison

### Database Costs

| Item | RDS (Current) | SQLite + Litestream |
|------|---------------|---------------------|
| Database instance | $27.53/mo | $0 |
| Storage (20GB) | $1.63/mo | $0 |
| S3 storage | $0 | ~$0.02/mo |
| S3 requests | $0 | ~$0.03/mo |
| **Total** | **~$29/mo** | **~$0.05/mo** |
| **Annual savings** | - | **~$347/year** |

### Compute Costs (with migration from Spot to On-Demand)

| Item | Spot (Current) | On-Demand + Savings Plan |
|------|----------------|--------------------------|
| 2× t4g.small instances | ~$5/mo (unreliable) | ~$17.50/mo (reliable) |
| Spot interruptions | Frequent | None |
| **Annual cost** | ~$60 | ~$210 |
| **Additional annual cost** | - | +$150 |

### Net Annual Savings

| Change | Impact |
|--------|--------|
| RDS → Litestream | -$347/year |
| Spot → On-Demand + Savings Plan | +$150/year |
| **Net savings** | **~$197/year** |
| **Plus**: Reliable compute, no spot interruptions | ✓ |

---

## Phase 6: Compute Migration (Spot → On-Demand + Savings Plan)

This phase migrates from unreliable spot instances to on-demand instances with a Savings Plan for cost optimization.

### 6.1 Update ASG Terraform Configuration

Update `operationcode_infra/terraform/asg.tf`:

```hcl
# https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-optimized_AMI.html#ecs-optimized-ami-linux
data "aws_ssm_parameter" "ecs_optimized_ami" {
  name = "/aws/service/ecs/optimized-ami/amazon-linux-2023/arm64/recommended"
}

# https://registry.terraform.io/modules/terraform-aws-modules/autoscaling/aws/latest
module "autoscaling" {
  source  = "terraform-aws-modules/autoscaling/aws"
  version = "~> 8.0"

  # CHANGED: Remove "-spot" from name since we're using on-demand now
  name             = local.name
  min_size         = 2
  max_size         = 2  # Fixed size for Savings Plan coverage
  desired_capacity = 2

  # CHANGED: Disable mixed instances policy - use single instance type
  use_mixed_instances_policy = false

  # CHANGED: Single instance type for predictable Savings Plan coverage
  instance_type = "t4g.small"

  image_id                        = jsondecode(data.aws_ssm_parameter.ecs_optimized_ami.value)["image_id"]
  user_data                       = base64encode(local.user_data)
  ignore_desired_capacity_changes = true
  key_name                        = "oc-ops"

  create_iam_instance_profile = true
  iam_role_name               = local.name
  iam_role_description        = "ECS role for ${local.name}"
  iam_role_policies = {
    AmazonEC2ContainerServiceforEC2Role = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
    AmazonSSMManagedInstanceCore        = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
  }

  vpc_zone_identifier = data.aws_subnets.use2.ids
  health_check_type   = "EC2"
  network_interfaces = [
    {
      delete_on_termination       = true
      device_index                = 0
      associate_public_ip_address = true
      ipv6_address_count          = 1
      security_groups             = [module.autoscaling_sg.security_group_id]
    }
  ]

  block_device_mappings = [
    {
      device_name = "/dev/xvda"
      no_device   = 0
      ebs = {
        delete_on_termination = true
        encrypted             = false
        volume_size           = 30
        volume_type           = "gp3"
      }
    }
  ]

  autoscaling_group_tags = {
    AmazonECSManaged = true
  }

  protect_from_scale_in = false
  enable_monitoring     = false

  enabled_metrics = [
    "GroupDesiredCapacity",
    "GroupInServiceCapacity",
    "GroupInServiceInstances",
    "GroupMaxSize",
    "GroupMinSize",
    "GroupPendingCapacity",
    "GroupPendingInstances",
    "GroupTerminatingCapacity",
    "GroupTerminatingInstances",
    "GroupTotalCapacity",
    "GroupTotalInstances"
  ]

  tags = local.tags
}
```

### 6.2 Apply Terraform Changes

```bash
cd /Users/irving/src/operationcode/operationcode_infra/terraform

# Plan the changes
terraform plan -out=compute.plan

# Review the plan - should show:
# - ASG configuration changes
# - New on-demand instances replacing spot instances

# Apply
terraform apply compute.plan
```

### 6.3 Purchase Compute Savings Plan

After the ASG is running on-demand, purchase a Savings Plan via the AWS Console:

1. Go to **AWS Cost Management** → **Savings Plans** → **Purchase Savings Plans**

2. Select:
   | Setting | Value |
   |---------|-------|
   | Savings Plan type | **Compute Savings Plans** |
   | Commitment term | **1 Year** |
   | Payment option | **No Upfront** |
   | Hourly commitment | **$0.024** |

3. Review and purchase

**Note**: The Savings Plan purchase is a billing commitment, not infrastructure. It cannot be managed via Terraform and must be renewed manually each year.

### 6.4 Verify Savings Plan Coverage

After purchase, verify coverage in the AWS Console:

```bash
# Check Savings Plans utilization (after a few hours of usage)
aws ce get-savings-plans-utilization \
  --time-period Start=$(date -u -v-1d +%Y-%m-%d),End=$(date -u +%Y-%m-%d) \
  --query 'Total.[Utilization.UtilizationPercentage,AmortizedCommitment.TotalAmortizedCommitment]'
```

Target: **>95% utilization** indicates proper coverage.

### 6.5 Set Renewal Reminder

Savings Plans expire after 1 year. Set a reminder:

```bash
# Add to your calendar or task manager:
# "Renew AWS Compute Savings Plan - $0.024/hr commitment"
# Date: 11 months from purchase date
```

---

## Appendix

### A. File Changes Summary

| File | Action |
|------|--------|
| `Dockerfile` | Modified - add Litestream |
| `src/docker-entrypoint.sh` | New - startup script |
| `src/litestream.yml` | New - Litestream config |
| `src/settings/environments/production.py` | Modified - SQLite support |
| `terraform/storage.tf` | New - S3 bucket |
| `terraform/iam.tf` | New - IAM policy |
| `terraform/python_backend/main.tf` | Modified - env vars |
| `terraform/asg.tf` | Modified - Spot → On-Demand |
| `scripts/migrate_pg_to_sqlite.sh` | New - migration script |

### B. Environment Variables

| Variable | Old Value | New Value |
|----------|-----------|-----------|
| `DB_ENGINE` | `django.db.backends.postgresql` | `django.db.backends.sqlite3` |
| `DB_NAME` | `operationcode` | `/data/db.sqlite3` |
| `LITESTREAM_ENABLED` | N/A | `true` |
| `DB_HOST` | (RDS endpoint) | N/A (removed) |
| `DB_USER` | (RDS user) | N/A (removed) |
| `DB_PASSWORD` | (RDS password) | N/A (removed) |

### C. Testing Locally

```bash
# Build and run with SQLite locally
docker-compose -f docker-compose.sqlite.yml up

# docker-compose.sqlite.yml
services:
  backend:
    build:
      context: .
      target: production
    environment:
      - SECRET_KEY=dev-secret-key
      - DJANGO_ENV=development
      - DEBUG=True
      - DB_ENGINE=django.db.backends.sqlite3
      - DB_NAME=/data/db.sqlite3
      - LITESTREAM_ENABLED=false
    ports:
      - "8000:8000"
    volumes:
      - sqlite_data:/data

volumes:
  sqlite_data:
```
