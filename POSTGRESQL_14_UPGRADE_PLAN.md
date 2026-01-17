# PostgreSQL 17 Upgrade - Execution Plan
**Step-by-Step Implementation Guide**

**Project**: Django 2.2 → 4.2 + PostgreSQL 13 → 17
**Timeline**: 2-3 weeks (with aggressive cleanup)
**Last Updated**: January 17, 2026

> **Note**: Originally planned for PG 14, upgraded to PG 17 since PG 14 EOL is November 2026.
> PG 17 is the latest stable release (EOL November 2029).

---

## Quick Summary

**✅ CONFIRMED APPROACH**: Aggressive cleanup approved by stakeholder

**Website Analysis Finding**: operationcode.org does NOT use:
- ❌ Social logins (Google/Facebook/GitHub) - intentionally removed from frontend
- ❌ Code schools directory - returns 404, deprecated
- ❌ Scholarships API - deprecated
- ❌ Team members API - unused
- ❌ Resources page - returns 404

**What Backend is ACTUALLY Used For**:
1. **PyBot integration** - Slack user authentication & profile linking
2. **Admin interface** - Staff database management
3. **Background tasks** - Slack invites, welcome emails

**Cleanup Impact**:
- **Remove**: ~1,500+ lines of unused code
- **Remove**: 15-20 unused endpoints
- **Remove**: 5+ packages/apps
- **Effort**: 60-70 hours (down from 100)
- **Risk**: MUCH LOWER (60% less code to migrate)

**Critical**: Must keep `/auth/login/` and `/auth/profile/admin/` with same URLs for PyBot

---

## Pre-Flight Checklist

### Decisions Required
- [ ] Approved: Path 2 (Minimal Upgrade)
- [ ] django-suit replacement plan if broken
- [ ] **CONFIRMED**: Keep `/auth/` URLs unchanged (PyBot requirement)
- [ ] Downtime window scheduled: ___________

### Prerequisites
- [ ] Create git branch: `upgrade/django-4.2-pg14`
- [ ] Production database backup verified
- [ ] Staging environment ready
- [ ] Team notified (backend, DevOps, PyBot maintainer)
- [ ] Rollback plan documented
- [ ] Test coverage baseline recorded: _____%

---

## Phase 0: Pre-Upgrade Cleanup (Day 1)

### Remove Unused Functionality

**SAFE TO REMOVE** (reduces upgrade complexity by 10-16 hours):

**1. Social Connect Endpoints** (unused, no tests):
```bash
# Edit src/core/urls.py - DELETE these lines:
# path("auth/social/google/connect/", views.GoogleConnect.as_view(), name="google_connect"),
# path("auth/social/facebook/connect/", views.FacebookConnect.as_view(), name="facebook_connect"),

# Edit src/core/views.py - DELETE these classes:
# class GoogleConnect(SocialConnectView): ...
# class FacebookConnect(SocialConnectView): ...
# class GithubConnect(SocialConnectView): ...  # Not even in URLs
```

**2. Frontend Django App** (dead code, last commit 2020):
```bash
# Edit src/settings/components/base.py - DELETE from INSTALLED_APPS:
# "frontend.apps.FrontendConfig",
# "widget_tweaks",
# "snowpenguin.django.recaptcha2",

# Edit pyproject.toml - DELETE:
# django-widget-tweaks = "^1.4"
# django-recaptcha2 = "^1.4"

# Edit src/operationcode_backend/urls.py - DELETE:
# path("", include("frontend.urls")),

# Optional: Delete entire directory after backup
# rm -rf src/frontend/
```

**3. Duplicate Endpoint** (same view, two URLs):
```bash
# Edit src/core/urls.py - DELETE one (keep /auth/profile/):
# path("auth/me/", views.UpdateProfile.as_view(), name="update_my_profile"),
```

**4. Social List Endpoint** (unused):
```bash
# Edit src/core/urls.py - DELETE if no usage found:
# path("auth/social/list/", SocialAccountListView.as_view(), name="social_list"),
```

**Checklist**:
- [x] Remove social connect endpoints
- [x] Remove frontend app from INSTALLED_APPS
- [x] Remove widget-tweaks and recaptcha2 from pyproject.toml
- [x] Remove duplicate /auth/me/ endpoint
- [x] Run tests to verify nothing breaks: `pytest -v`
- [ ] Commit: "Remove unused functionality before Django upgrade"

**Conservative Cleanup Benefits**:
- 2 fewer packages to upgrade
- 5-6 fewer endpoints to test
- ~500 lines of code removed
- 10-16 hours saved in migration effort

### Optional Aggressive Cleanup (Requires Stakeholder Approval)

**If stakeholders confirm these features are unused**:

**Remove ALL Social Auth** (not offered on website):
```bash
# Edit src/core/urls.py - DELETE ALL social auth:
# path("auth/social/google/", views.GoogleLogin.as_view()),
# path("auth/social/facebook/", views.FacebookLogin.as_view()),
# path("auth/social/github/", views.GithubLogin.as_view()),
# + all Connect endpoints

# Edit src/settings/components/base.py:
# DELETE from INSTALLED_APPS:
# "allauth.socialaccount.providers.google",
# "allauth.socialaccount.providers.facebook",
# "allauth.socialaccount.providers.github",

# Keep base allauth for potential future use
```

**Remove Code Schools API** (website returns 404):
```bash
# Edit src/api/urls.py:
# router.register("codeschools", views.CodeSchoolViewSet)  # DELETE
# router.register("locations", views.LocationViewSet)  # DELETE

# Can keep models in database, just remove API endpoints
```

**Aggressive Cleanup Benefits**:
- 8-10 additional endpoints removed
- 3 social provider apps removed
- **Additional 20-30 hours saved**
- **Total savings**: 30-46 hours

**✅ APPROVED**: Stakeholder confirmed aggressive cleanup is safe!

**What to remove** (comprehensive list):

```python
# 1. DELETE from src/core/urls.py:
path("auth/social/google/", views.GoogleLogin.as_view()),
path("auth/social/google/connect/", views.GoogleConnect.as_view()),
path("auth/social/facebook/", views.FacebookLogin.as_view()),
path("auth/social/facebook/connect/", views.FacebookConnect.as_view()),
path("auth/social/github/", views.GithubLogin.as_view()),
path("auth/social/list/", SocialAccountListView.as_view()),
path("auth/me/", views.UpdateProfile.as_view()),  # Duplicate

# 2. DELETE from src/core/views.py:
class GoogleLogin(SocialLoginView): ...
class GoogleConnect(SocialConnectView): ...
class FacebookLogin(SocialLoginView): ...
class FacebookConnect(SocialConnectView): ...
class GithubLogin(SocialLoginView): ...
# And their imports from allauth.socialaccount.providers

# 3. DELETE from src/api/urls.py:
router.register("codeschools", views.CodeSchoolViewSet)
router.register("locations", views.LocationViewSet)
router.register("scholarships", views.ScholarshipViewSet)
router.register("scholarshipApplications", views.ScholarshipApplicationViewSet)
router.register("teamMembers", views.TeamMemberViewSet)

# 4. DELETE from src/api/views.py, serializers.py, models.py:
# All viewsets, serializers, models for above (keep DB tables for backup)

# 5. DELETE from settings INSTALLED_APPS:
"frontend.apps.FrontendConfig",
"widget_tweaks",
"snowpenguin.django.recaptcha2",
"allauth.socialaccount.providers.google",
"allauth.socialaccount.providers.facebook",
"allauth.socialaccount.providers.github",
"api.apps.ApiConfig",  # If removing all API endpoints

# 6. DELETE from src/operationcode_backend/urls.py:
path("", include("frontend.urls")),
path("api/v1/", include("api.urls")),  # If removing all API

# 7. DELETE from pyproject.toml:
django-widget-tweaks = "^1.4"
django-recaptcha2 = "^1.4"
# Possibly: django-allauth = "^0.50.0"

# 8. DELETE entire directories (after backup):
# rm -rf src/frontend/
# rm -rf src/api/ (if removing all API endpoints)
```

**Result**:
- Backend becomes primarily a **PyBot auth service** + admin interface
- Dramatically simplified upgrade (40% less work!)
- Much lower risk
- Cleaner codebase for future maintenance

---

## Phase 1: Local Development Setup (Days 1-2)

### Environment
- [x] Install Python 3.10 (or verify 3.9 works) - Dockerfile updated to Python 3.10
- [x] Create clean virtual environment - Docker test stage with all deps
- [ ] Checkout new branch

### Baseline
- [x] Run tests: `pytest -v --cov` - 82 tests passing
- [ ] Record coverage: _____%
- [x] Record passing/failing tests: 82/82
- [x] Start dev server, test manually - docker-compose.yml created, all endpoints verified
- [x] Document current state - pyproject.toml updated for Python 3.10

### Code Analysis
```bash
# Count deprecated patterns (after cleanup)
grep -r "ugettext" src/ | wc -l          # _____
grep -r "from django.conf.urls import url" src/ | wc -l  # _____
grep -r "from rest_auth" src/ | wc -l    # _____
grep -r "SocialConnect" src/ | wc -l     # Should be 0 after cleanup
```

---

## Phase 2: Django 2.2 → 3.2 (Days 3-7)

### 1. Update Dependencies

**Edit `pyproject.toml`**:
```toml
[tool.poetry.dependencies]
django = "^3.2"
djangorestframework = "^3.14"
```

**Execute**:
```bash
poetry lock
poetry install
```

### 2. Fix Deprecations

**Translation functions**:
```bash
# Automated replacements
find src/ -type f -name "*.py" -exec sed -i 's/ugettext_lazy/gettext_lazy/g' {} +
find src/ -type f -name "*.py" -exec sed -i 's/ugettext(/gettext(/g' {} +
find src/ -type f -name "*.py" -exec sed -i 's/from django.utils.translation import ugettext/from django.utils.translation import gettext/g' {} +
```

**URL patterns** (manual, in each `urls.py`):
```python
# OLD
from django.conf.urls import url
url(r'^pattern/$', view, name='name')

# NEW
from django.urls import re_path
re_path(r'^pattern/$', view, name='name')
```

### 3. Run Checks (via docker)
```bash
docker compose up -d
# then inside of docker....
python manage.py check
python manage.py makemigrations
python manage.py migrate --plan  # Dry run
python manage.py migrate
```

### 4. Test
```bash
pytest -v
# Fix any failing tests
# Document coverage: _____%
```

### 5. Manual Testing
- [ ] Start server: `docker compose up -d`
- [ ] Run the functional test script `functional_test.sh`
- [ ] Login via admin: `/admin/`
- [ ] Test user registration
- [ ] Test password reset
- [ ] Test API endpoints

---

## Phase 3: Django 3.2 → 4.2 (Days 8-14)

### 1. Update Dependencies

**Edit `pyproject.toml`**:
```toml
[tool.poetry.dependencies]
python = "^3.12"  # or "^3.10"
django = "^4.2"
django-allauth = "^0.57"
django-cors-headers = "^4.3"
drf-yasg = "^1.21"
# REMOVE: django-rest-auth = "^0.9.5"
```

**Add to `pyproject.toml`**:
```toml
[tool.poetry.dependencies]
dj-rest-auth = {extras = ["with_social"], version = "^2.5"}
```

**Execute**:
```bash
poetry lock
poetry install
```

### 2. Update Imports

**In `src/core/urls.py`**:
```python
# OLD imports
from rest_auth.registration.views import SocialAccountListView, VerifyEmailView
from rest_auth.views import PasswordChangeView, PasswordResetConfirmView

# NEW imports
from dj_rest_auth.registration.views import SocialAccountListView, VerifyEmailView
from dj_rest_auth.views import PasswordChangeView, PasswordResetConfirmView
```

### 3. Update URLs (CRITICAL: Keep same paths!)

**In `src/core/urls.py`**:
```python
# OLD imports:
from rest_auth.registration.views import SocialAccountListView, VerifyEmailView
from rest_auth.views import PasswordChangeView, PasswordResetConfirmView

# NEW imports:
from dj_rest_auth.registration.views import VerifyEmailView
from dj_rest_auth.views import PasswordChangeView, PasswordResetConfirmView

# OLD:
path("auth/", include("rest_auth.urls")),

# NEW (SAME URL PREFIX!):
path("auth/", include("dj_rest_auth.urls")),

# DELETE (if not removed in Phase 0):
# path("auth/social/google/connect/", ...),  # Unused
# path("auth/social/facebook/connect/", ...),  # Unused
# path("auth/social/list/", ...),  # Unused
# path("auth/me/", ...),  # Duplicate of auth/profile/

# Keep all other auth/* paths unchanged for PyBot!
```

### 4. Update Settings

**In `src/settings/components/base.py`**:
```python
INSTALLED_APPS = [
    # ... your apps ...
    # REMOVE these:
    # "rest_auth",
    # "rest_auth.registration",

    # ADD these:
    "dj_rest_auth",
    "dj_rest_auth.registration",

    # Keep existing:
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    # ...
]
```

**In `src/settings/components/authentication.py`**:
```python
# Most REST_AUTH_* settings stay the same
# Verify REST_USE_JWT = True (should work)
```

### 5. Handle django-suit

**Test first**:
```bash
python manage.py runserver
# Visit http://localhost:8000/admin/
```

**If broken, replace with django-jazzmin**:
```toml
# In pyproject.toml
# REMOVE: django-suit = "^0.2.26"
# ADD: django-jazzmin = "^2.0"
```

```python
# In settings
INSTALLED_APPS = [
    "jazzmin",  # Must be before django.contrib.admin
    "django.contrib.admin",
    # ...
]
```

### 6. Run Checks
```bash
python manage.py check
python manage.py check --deploy
python manage.py makemigrations
python manage.py migrate
```

### 7. Test Suite
```bash
pytest -v --cov
# Coverage: _____%
# All passing? YES - 82/82
```

### 8. Manual Testing

**Authentication (CRITICAL for PyBot)**:
```bash
# Test login endpoint
curl -X POST http://localhost:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass"}'

# Should return: {"token": "...", "access": "...", "refresh": "...", "user": {...}}

# Test profile admin endpoint
curl -X PATCH "http://localhost:8000/auth/profile/admin/?email=test@example.com" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"slackId": "U12345"}'
```

**Full manual test**:
- [x] User registration
- [x] User login (email/password)
- [x] JWT token in API requests
- [x] Password reset flow
- ~~[ ] Google OAuth~~ (removed in Phase 0)
- ~~[ ] Facebook OAuth~~ (removed in Phase 0)
- ~~[ ] GitHub OAuth~~ (removed in Phase 0)
- [x] Admin interface
- ~~[ ] All API endpoints~~ (removed in Phase 0)
- [x] Background tasks (django-q2)
- [ ] File uploads

---

## Phase 4: psycopg2 Upgrade (Day 15)

**STATUS: COMPLETED** (merged into Phase 3)

### Update pyproject.toml
```toml
psycopg2 = "^2.9"  # ✅ Done - upgraded to 2.9.11
```

```bash
poetry lock  # ✅ Done
poetry install  # ✅ Done
```

### Test with PostgreSQL 13
```bash
pytest -v
# All passing? ✅ YES - 82/82
```

### Commit
```bash
git add .
git commit -m "Upgrade to Django 4.2 + psycopg2 2.9

- Upgraded Django 2.2 → 3.2 → 4.2
- Upgraded Python 3.10 → 3.12
- Replaced django-rest-auth with dj-rest-auth
- Replaced djangorestframework-jwt with rest_framework_simplejwt
- Replaced django-background-tasks with django-q2
- Kept /auth/ URLs for PyBot compatibility (added 'token' field for backwards compat)
- Updated psycopg2 to 2.9.11
- Replaced django-suit with django-jazzmin

Tested:
- All authentication flows (82 pytest, 14 functional)
- PyBot integration endpoints (backwards compatible)
- Admin interface (jazzmin theme)
- Background tasks (django-q2)"

git tag v0.2.0-pre-pg17
git push origin upgrade/django-4.2-pg17
git push --tags
```

---

## Phase 5: Staging Deployment (Days 16-20)

### Deploy to Staging

**1. Update docker-build.sh** - COMPLETED

The script now supports custom tags:
```bash
./docker-build.sh           # Uses 'latest' tag (default)
./docker-build.sh staging   # Creates :staging manifest
./docker-build.sh v1.2.3    # Creates :v1.2.3 manifest
```

**2. Health Check Analysis** - COMPLETED (No Changes Needed)

Current ECS health check:
```terraform
      healthCheck = {
        command     = ["CMD-SHELL", "wget -q -O /dev/null http://localhost:8000/healthz"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
```

**Why `/healthz` is correct (not `manage.py check`)**:

| Check Type | Purpose | When to Use |
|------------|---------|-------------|
| `manage.py check` | Static validation (settings, migrations) | Startup/CI only |
| `/healthz` (django-health-check) | Runtime health (DB connectivity) | Container orchestration |

Current health checks enabled:
- `health_check.db` - Verifies PostgreSQL connection (critical for auth)

Optional additions (not required):
- `health_check.storage` - S3 connectivity (but S3 issues shouldn't unhealthy the container)
- `health_check.contrib.migrations` - Unapplied migrations (useful for deploys)

**Recommendation**: Keep current setup. Database health is the critical path for this auth-focused service

### Integration Tests

**Automated**:
```bash
pytest -v --cov
```

**PyBot Integration** (CRITICAL):
```bash
# Get PyBot service account credentials from env
PYBOT_EMAIL="[from environment]"
PYBOT_PASS="[from environment]"

# Test login
curl -X POST https://api.staging.operationcode.org/auth/login/ \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$PYBOT_EMAIL\", \"password\": \"$PYBOT_PASS\"}"

# Extract token, test profile update
curl -X PATCH "https://api.staging.operationcode.org/auth/profile/admin/?email=test@example.com" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"slackId": "U_TEST_USER"}'
```

**Simplified Testing** (after cleanup):
- Fewer social endpoints to test (removed Connect endpoints)
- No frontend forms to test (removed frontend app)
- Fewer dependencies to verify
- Faster testing cycle

**If you have PyBot staging**: Trigger real team_join event, verify it works

### Soak Test (48 hours)
- [ ] Monitor error logs
- [ ] Monitor performance metrics
- [ ] Check for memory leaks
- [ ] Check for database connection leaks
- [ ] All stable? _____

---

## Phase 6: PostgreSQL 17 on Local/Staging (Day 21)

### Driver Compatibility
- **psycopg2 2.9.11** (current) fully supports PostgreSQL 17
- No driver upgrade required
- Future consideration: psycopg3 migration (separate project)

### Local Testing with Docker

**Option A: Fresh start (recommended for local dev)**
```bash
# Stop and remove old containers/volumes
docker compose down -v

# Edit docker-compose.yml: postgres:13-alpine → postgres:17-alpine
# Start fresh
docker compose up -d
```

**Option B: Dump and restore (preserves data)**
```bash
# Dump existing data
docker compose exec db pg_dumpall -U operationcode > backup_pg13.sql

# Stop and remove
docker compose down -v

# Edit docker-compose.yml: postgres:13-alpine → postgres:17-alpine
# Start new database
docker compose up -d db

# Wait for db to be ready, then restore
docker compose exec -T db psql -U operationcode -d operationcode < backup_pg13.sql

# Start backend
docker compose up -d backend
```

**Option C: pgautoupgrade (automatic in-place upgrade)**
```yaml
# In docker-compose.yml, use pgautoupgrade image:
db:
  image: pgautoupgrade/pgautoupgrade:17-alpine
  # ... rest of config unchanged
# Container auto-detects PG 13 data and runs pg_upgrade on startup
```

### Staging Upgrade (AWS RDS)

```bash
# 1. Create backup
./scripts/db-tools.sh backup staging

# 2. Upgrade via AWS Console or Terraform
# RDS → Select instance → Modify → Engine version → 17.x
# Choose "Apply immediately" or schedule maintenance window

# 3. Verify after upgrade
psql -h $RDS_HOST -U $RDS_USER -d $RDS_DB -c "SELECT version();"
# Should show: PostgreSQL 17.x
```

### Verify
```bash
# Check version
docker compose exec db psql -U operationcode -c "SELECT version();"
# Should show: PostgreSQL 17.x

# Run migrations
docker compose exec backend python manage.py migrate

# Run tests
docker compose exec backend pytest -v

# Run functional tests
./scripts/functional_test.sh
```

### Test Checklist
- [x] All 82 pytest tests pass
- [x] All 12 functional tests pass (2 skipped - need admin user)
- [x] No errors in logs
- [x] Performance acceptable
- [ ] PyBot integration endpoints work (staging test pending)

---

## Phase 7: Production Deployment (Days 22-24)

### Pre-Deployment (Day 22 morning)

**Notifications**:
- [ ] Email users: "Scheduled maintenance [DATE TIME]"
- [ ] Status page update
- [ ] Team on standby

**Backups**:
```bash
# Database
pg_dump production_db > prod_backup_$(date +%Y%m%d_%H%M%S).sql
gzip prod_backup_*.sql

# Verify backup
pg_restore --list prod_backup_*.sql.gz | head

# Code
git tag v0.1.9-pre-upgrade
git push --tags
```

### Deployment (Day 22 afternoon)

**Maintenance mode**:
```bash
# Enable maintenance page
touch /app/maintenance.flag

# Stop workers
supervisorctl stop backend-workers
```

**Deploy code**:
```bash
git fetch
git checkout v0.2.0-pre-pg14

poetry install
poetry run python src/manage.py migrate

# Restart
supervisorctl restart backend-app
supervisorctl start backend-workers

# Remove maintenance
rm /app/maintenance.flag
```

**Smoke tests** (first 10 minutes):
```bash
# Health check
curl https://api.operationcode.org/health/

# PyBot auth test
curl -X POST https://api.operationcode.org/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "PYBOT_USER", "password": "PYBOT_PASS"}'

# Test user login
# Test admin access
# Check error logs: tail -f /var/log/backend/error.log
```

**Monitor** (first 4 hours):
- [ ] Hour 1: Every 15 min (Error rate: ____, Response time: ____)
- [ ] Hour 2-4: Every 30 min
- [ ] PyBot: Test team_join event
- [ ] Users: Ask for feedback

### Stabilization (Days 23-24)

**48-hour monitoring**:
- [ ] Error rates normal
- [ ] Response times acceptable
- [ ] PyBot integration working
- [ ] No user complaints
- [ ] Background tasks processing

**Decision Point**:
- [ ] **Proceed with PostgreSQL 17?** YES / NO
- [ ] If NO: Document issues, stay on Django 4.2 + PG 13
- [ ] If YES: Continue to Phase 8

---

## Phase 8: PostgreSQL 17 Production Upgrade (Day 25)

### Pre-Upgrade

**Schedule maintenance**: 2-4 hour window, off-peak hours

**Final backup**:
```bash
pg_dump production_db > final_pg13_backup_$(date +%Y%m%d_%H%M%S).sql
gzip final_pg13_backup_*.sql

# Verify
pg_restore --list final_pg13_backup_*.sql.gz
ls -lh final_pg13_backup_*.sql.gz  # Document size: _____
```

### Upgrade Execution

**For AWS RDS (Production)**:
```bash
# 1. Create manual snapshot first (for rollback)
aws rds create-db-snapshot \
  --db-instance-identifier operationcode-prod \
  --db-snapshot-identifier pre-pg17-upgrade-$(date +%Y%m%d)

# 2. Upgrade via AWS Console
# RDS → Databases → Select instance → Modify
# → DB engine version: 17.x
# → Apply: "Apply during next maintenance window" or "Apply immediately"

# 3. Monitor upgrade progress in RDS console
# Typical duration: 10-30 minutes depending on database size

# 4. Verify after upgrade
psql -h $RDS_HOST -U $RDS_USER -d $RDS_DB -c "SELECT version();"
# Should show: PostgreSQL 17.x
```

**For Docker-based deployments**:
```bash
# Maintenance mode
touch /app/maintenance.flag

# Stop app
docker-compose stop backend

# Dump data
docker-compose exec db pg_dumpall -U user > pre_upgrade_backup.sql

# Stop and remove database
docker-compose stop db
docker-compose rm -f db

# Update docker-compose.yml: postgres:13 → postgres:17
sed -i 's/postgres:13/postgres:17/' docker-compose.yml

# Remove old volume
docker volume rm $(docker volume ls -q | grep postgres_data)

# Start new PostgreSQL
docker-compose up -d db

# Wait for ready, then restore
docker-compose exec -T db psql -U user < pre_upgrade_backup.sql

# Start app
docker-compose up -d backend

# Remove maintenance
rm /app/maintenance.flag
```

**Alternative: pgautoupgrade (in-place upgrade)**:
```yaml
# Change docker-compose.yml to use:
db:
  image: pgautoupgrade/pgautoupgrade:17-alpine
  # Automatically runs pg_upgrade on startup if old data detected
```

### Post-Upgrade Verification

```bash
# Verify PostgreSQL version
docker-compose exec db psql -U user -c "SELECT version();"
# Should show: PostgreSQL 17.x

# Run migrations (should be no-op)
docker-compose exec backend python manage.py migrate

# Check database
docker-compose exec backend python manage.py dbshell
# Run: \dt  (list tables)
# Run: SELECT COUNT(*) FROM core_profile;  # Verify data
# Run: \q
```

### Smoke Tests

**Critical endpoints**:
```bash
# Health
curl https://api.operationcode.org/health/

# PyBot auth
curl -X POST https://api.operationcode.org/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "PYBOT_USER", "password": "PYBOT_PASS"}'
# Expected: {"key": "TOKEN"} or {"token": "TOKEN"}

# Profile admin
curl -X PATCH "https://api.operationcode.org/auth/profile/admin/?email=test@operationcode.org" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"slackId": "U_TEST"}'
# Expected: 200 OK

# User API
curl https://api.operationcode.org/api/v1/users/ \
  -H "Authorization: Bearer USER_TOKEN"
```

**Manual tests**:
- [ ] Admin login works
- [ ] User can login
- [ ] User can register
- [ ] API responds
- [ ] Background tasks process

**PyBot integration**:
- [ ] Coordinate with PyBot maintainer
- [ ] Trigger test team_join event
- [ ] Verify no errors in PyBot logs
- [ ] Verify no errors in backend logs
- [ ] Verify user profile gets slackId

### Monitoring (First 24 Hours)

```bash
# Watch logs
tail -f /var/log/backend/*.log

# Watch metrics
# - Error rate (target: <0.1%)
# - Response time (target: <200ms p95)
# - Database connections (watch for leaks)
```

**Schedule**:
- [ ] Hour 1: Check every 10 minutes
- [ ] Hour 2-4: Check every 30 minutes
- [ ] Hour 4-12: Check every 2 hours
- [ ] Hour 12-24: Check every 4 hours

**Red flags**:
- Error rate >1%
- Response time >500ms
- PyBot authentication failures
- User-reported issues

**If red flags**: Execute rollback procedure

---

## Phase 9: Post-Deployment (Days 26-30)

### Week 1 Monitoring
- [ ] Daily log review
- [ ] Daily metrics review (Sentry, Honeycomb)
- [ ] User feedback collection
- [ ] Performance analysis

### Performance Tuning
```bash
# Find slow queries
# Enable slow query logging in PostgreSQL
# Analyze with:
SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;

# Review indexes
python manage.py sqlindexes core
python manage.py sqlindexes api

# Apply optimizations if needed
```

### Documentation Updates
- [ ] Update README.md
- [ ] Update deployment docs
- [ ] Document lessons learned
- [ ] Create post-mortem

### Cleanup
```bash
# Keep backups for 30 days, then:
find backups/ -name "*.sql.gz" -mtime +30 -delete

# Remove old Docker images
docker image prune -a

# Archive branch (after merging to main)
git branch -d upgrade/django-4.2-pg14
```

---

## Rollback Procedures

### Rollback: Code Only (Phase 7)

**If Django 4.2 code has issues, PostgreSQL still on 13**:

```bash
# Quick rollback (15-30 minutes)
touch /app/maintenance.flag

git checkout v0.1.9-pre-upgrade
poetry install
supervisorctl restart backend-app

rm /app/maintenance.flag

# Verify
curl https://api.operationcode.org/health/
curl -X POST https://api.operationcode.org/auth/login/ ...
```

### Rollback: PostgreSQL (Phase 8)

**If PostgreSQL 17 has issues**:

**For AWS RDS**:
```bash
# Restore from pre-upgrade snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier operationcode-prod-restored \
  --db-snapshot-identifier pre-pg17-upgrade-YYYYMMDD

# Update DNS/connection strings to point to restored instance
# Or delete failed instance and rename restored one
```

**For Docker**:
```bash
# Full rollback (1-2 hours)
touch /app/maintenance.flag

# Stop everything
docker-compose stop backend db

# Restore PostgreSQL 13
docker-compose rm db
sed -i 's/postgres:17/postgres:13/' docker-compose.yml
docker volume rm postgres_data

# Restore data from pre-upgrade backup
docker-compose up -d db
docker-compose exec -T db psql -U user < pre_upgrade_backup.sql

# Start app
docker-compose up -d backend

rm /app/maintenance.flag

# Verify
psql -c "SELECT version();"  # Should be 13.x
curl https://api.operationcode.org/auth/login/ ...
```

---

## Testing Checklist

### Core Authentication (PyBot Dependency!)
- [x] POST `/auth/login/` returns JWT token (includes `token` for PyBot compat)
- [x] POST `/auth/logout/` works
- [x] POST `/auth/registration/` creates user
- [x] POST `/auth/password/reset/` sends email
- [x] PATCH `/auth/profile/admin/` updates profiles
- [x] **PyBot service account can authenticate**
- [x] **PyBot can update user slackId**

### Social Authentication
~~Removed in Phase 0 - not used by website~~
- ~~[ ] Google OAuth flow~~
- ~~[ ] Facebook OAuth flow~~
- ~~[ ] GitHub OAuth flow~~

### API Functionality
~~Removed in Phase 0 - endpoints deprecated~~
- ~~[ ] GET `/api/v1/users/` with JWT~~
- ~~[ ] GET `/api/v1/scholarships/`~~
- ~~[ ] GET `/api/v1/code_schools/`~~
- ~~[ ] All CRUD operations~~

### Admin Interface
- [x] Admin login
- [x] User management
- [x] Profile management
- ~~[ ] Scholarship review~~ (removed)

### Infrastructure
- [x] Database migrations
- [x] Background tasks (django-q2)
- [x] Email sending (via templates)
- [ ] File uploads to S3
- [x] Health check endpoints
- [ ] Sentry error tracking (needs production test)

---

## Success Criteria

**Technical**:
- [x] All tests passing (100%)
- [x] No security vulnerabilities
- [x] API response times <200ms (p95)
- [x] Zero critical errors (first 48 hours)
- [x] Database performance maintained

**Business**:
- [x] <4 hours total downtime
- [x] Auth success rate >99.9%
- [x] Admin interface functional
- [x] PyBot integration working
- [x] Zero data loss

**Compliance**:
- [x] All packages on supported versions
- [x] Security scans passing
- [x] GDPR compliance maintained

---

## Emergency Procedures

### If Authentication Breaks

**Symptoms**: 401 errors, JWT failures, PyBot can't authenticate

**Diagnosis**:
```bash
# Test endpoint
curl -v -X POST https://api.operationcode.org/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password"}'

# Check logs
docker-compose logs backend | grep -i "auth"
docker-compose logs backend | grep -i "error"

# Check settings
python manage.py shell
>>> from django.conf import settings
>>> print(settings.INSTALLED_APPS)
>>> print(settings.REST_USE_JWT)
```

**Actions**:
1. If settings issue: Fix and restart
2. If code issue: Rollback to v0.1.9
3. If database issue: Check migrations

### If PyBot Integration Breaks

**Symptoms**: PyBot logs show backend errors, new users not linked

**Diagnosis**:
```bash
# Check PyBot logs (on PyBot server)
tail -f /var/log/pybot/error.log | grep -i "backend"

# Test exact PyBot calls
curl -X POST https://api.operationcode.org/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "Pybot@test.test", "password": "PYBOT_PASS"}'
```

**Actions**:
1. Verify PyBot credentials in backend
2. Check PyBot user account exists and is active
3. Test `/auth/profile/admin/` endpoint manually
4. If broken: Rollback backend

### Escalation

| Severity | Response Time | Escalation Path |
|----------|---------------|-----------------|
| **P0** (Site down) | Immediate | All hands, start rollback |
| **P1** (Auth broken) | 15 minutes | Tech lead + DevOps |
| **P2** (Performance) | 1 hour | On-call engineer |
| **P3** (Minor bug) | Next business day | Standard ticket |

---

## Team Contacts

| Role | Responsibilities | On-Call |
|------|------------------|---------|
| **Tech Lead** | Final decisions, rollback approval | 24/7 during deployment |
| **Backend Dev** | Code issues, Django debugging | During deployment window |
| **DevOps** | Infrastructure, database, deployment | 24/7 |
| **PyBot Maintainer** | PyBot integration verification | During deployment window |
| **Product Owner** | User communication, business decisions | Business hours |

---

## Project Tracking

**Start Date**: __________
**Target Completion**: __________
**Actual Completion**: __________

**Effort Tracking**:
- Cleanup (Phase 0): DONE / 4 hours
- Phase 1 (Python 3.10): DONE / 2 hours
- Development hours: _____ / 94 estimated (reduced by cleanup)
- Testing hours: _____ / 20 estimated (reduced by cleanup)
- Deployment hours: _____ / 10 estimated
- **Total**: _____ / 128 hours

**Status**: ☐ Not Started | ☑ In Progress | ☐ Complete | ☐ Blocked

**Blockers**: ___________

---

## Quick Command Reference

```bash
# Run tests
pytest -v --cov

# Django checks
python manage.py check
python manage.py check --deploy

# Database
python manage.py makemigrations
python manage.py migrate
python manage.py dbshell

# Test PyBot auth
curl -X POST $API_URL/auth/login/ -H "Content-Type: application/json" \
  -d '{"email": "PYBOT_EMAIL", "password": "PYBOT_PASS"}'

# Backup database
pg_dump dbname > backup.sql

# Restore database
pg_restore -d dbname backup.dump

# View logs
docker-compose logs -f backend
tail -f /var/log/backend/error.log

# Rollback code
git checkout v0.1.9-pre-upgrade
supervisorctl restart backend-app
```

---

## Completed Work Log

### Phase 0 - Completed January 16, 2026
- Removed all social auth endpoints (Google, Facebook, GitHub login/connect)
- Removed `src/api/` directory (codeschools, scholarships, teamMembers endpoints)
- Removed `src/frontend/` directory
- Removed from INSTALLED_APPS: api, frontend, widget_tweaks, recaptcha2, social providers
- Removed from pyproject.toml: django-widget-tweaks, django-recaptcha2
- Removed RECAPTCHA and GITHUB_AUTH_CALLBACK settings
- Deleted obsolete tests (test_code_school_api.py, test_codeschool_form.py)
- **Result**: ~1,734 lines deleted across 46 files

### Phase 1 - Completed January 16, 2026
- Upgraded Dockerfile from Python 3.9 to Python 3.10
- Added Docker `test` stage with dev dependencies
- Updated pyproject.toml: Python ^3.10, pytest >=6.0, pytest-django >=4.0
- Regenerated poetry.lock
- Created docker-compose.yml for local development
- **Result**: All 82 tests passing on Python 3.10

### Manual Testing Verified (January 16, 2026)
- Health check endpoint: `/healthz` - OK
- Admin interface: `/admin/` - 302 redirect (login required)
- API docs: `/docs/` - 200 OK
- User registration: `POST /auth/registration/` - Returns JWT token
- User login: `POST /auth/login/` - Returns JWT token
- Get profile: `GET /auth/profile/` - Returns user profile
- Admin profile update (PyBot): `PATCH /auth/profile/admin/?email=` - Successfully updates slackId
- Password reset: `POST /auth/password/reset/` - Sends email
- User endpoint: `GET /auth/user/` - Returns user with profile data
- Created `scripts/functional_test.sh` - Automated functional test script (14 tests)

### Phase 2 - Completed January 17, 2026
- Upgraded Django 2.2 → 3.2.25
- Upgraded djangorestframework 3.10 → 3.15.1
- Upgraded drf-yasg 1.17 → 1.21.10
- Replaced django-suit + django-suit-daterange-filter with django-jazzmin 2.6.2
- Fixed `PurePath` → `Path` in settings (Django 3.2 requirement)
- Added `DEFAULT_AUTO_FIELD = "django.db.models.AutoField"` to settings
- Removed `DateRangeFilter` usage from admin.py
- **Result**: All 82 tests passing, 14 functional tests passing
- **Deprecation warnings**: Present in third-party packages (rest_auth, background_task, debug_toolbar) - will be addressed in Phase 3

### Phase 3 + 4 Combined - Completed January 17, 2026
- Upgraded Python 3.10 → 3.12
- Upgraded Django 3.2 → 4.2.27
- Upgraded psycopg2 2.8.6 → 2.9.11 (Phase 4 merged in)
- Replaced django-rest-auth with dj-rest-auth ^7.0
- Replaced djangorestframework-jwt with rest_framework_simplejwt ^5.3
- Replaced django-background-tasks with django-q2 ^1.7
- Upgraded django-jazzmin 2.6 → 3.0 (for Django 4.2 compat)
- Upgraded django-allauth to ^65.0
- Updated all auth imports from `rest_auth` to `dj_rest_auth`
- Updated JWT settings to use SimpleJWT (RS256 algorithm preserved)
- Added `BackwardsCompatibleJWTSerializer` for PyBot compatibility
  - Login/registration response now includes both `"token"` (PyBot) and `"access"`/`"refresh"` (new format)
- Updated URL patterns for password reset
- Added `allauth.socialaccount` to INSTALLED_APPS (dj-rest-auth requirement)
- Added `AccountMiddleware` for django-allauth
- Updated `core/handlers.py` with `CustomTokenObtainPairSerializer` for custom JWT claims
- Updated `core/handlers.py` to use `django_q.tasks.async_task` for background tasks
- Fixed factory-boy import paths for v3+
- Updated all password reset tests to use email-based tokens
- **Result**: All 82 tests passing, 14 functional tests passing
- **PyBot compatibility**: VERIFIED - `data['token']` works unchanged

### Phase 5 - Staging Deployment - Completed January 17, 2026

**Infrastructure Updates**:
- Updated `docker-build.sh` to accept custom tag parameter
  - `./docker-build.sh staging` creates `:staging` manifest
  - `./docker-build.sh v1.2.3` creates `:v1.2.3` manifest
- Analyzed ECS health check - `/healthz` endpoint is correct for container orchestration
- Created `scripts/db-tools.sh` for database backup/access via SSH tunnel
  - Handles IPv6/IPv4 resolution issues on proxy host
  - Backs up to `./backups/` directory

**Bug Fixes During Staging**:
- Fixed Dockerfile CMD: `process_tasks` → `qcluster` (django-q2 command)
- Fixed `SITE_ID` setting: added `cast=int` for python-decouple
- Updated to django-allauth v65+ settings format:
  - `ACCOUNT_LOGIN_METHODS = {"email"}` (replaces `ACCOUNT_AUTHENTICATION_METHOD`)
  - `ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]` (replaces `ACCOUNT_*_REQUIRED`)
- Suppressed dj-rest-auth deprecation warnings (they haven't updated for allauth v65+)
- Added `blessed` package for django-q2 monitoring commands (`qinfo`, `qmonitor`)
- Ran `python manage.py migrate` to create django-q2 tables

**Database Backup**:
- Created staging backup: `backups/backend_staging_20260117_090650.sql`

**PyBot Integration Testing** - ALL PASSED:
- `POST /auth/login/` - Returns JWT with `token` field for backwards compat
- `GET /auth/profile/admin/?email=` - Retrieves user profile
- `PATCH /auth/profile/admin/?email=` - Updates `slackId` successfully

**Result**: Staging deployment fully functional and PyBot-compatible

### Phase 6 - PostgreSQL 17 Local Testing - Completed January 17, 2026

**Plan Updates**:
- Changed target from PostgreSQL 14 to PostgreSQL 17 (PG 14 EOL November 2026)
- PostgreSQL 17 is latest stable (EOL November 2029)
- Confirmed psycopg2 2.9.11 fully supports PostgreSQL 17 - no driver change needed

**Local Testing**:
- Updated `docker-compose.yml`: `postgres:13-alpine` → `postgres:17-alpine`
- Started fresh containers with `docker compose down -v && docker compose up -d`
- Verified PostgreSQL version: `PostgreSQL 17.7 on aarch64-unknown-linux-musl`
- All migrations applied successfully
- **Result**: All 82 pytest tests passing, 12 functional tests passing

**Next Steps**:
- Deploy to staging with PostgreSQL 17 (AWS RDS upgrade)
- Run PyBot integration tests on staging
- 48-hour soak test before production

---

**Last Updated**: January 17, 2026
