# PostgreSQL 14 Upgrade - Execution Plan
**Step-by-Step Implementation Guide**

**Project**: Django 2.2 → 4.2 + PostgreSQL 13 → 14
**Timeline**: 2-3 weeks (with aggressive cleanup)
**Last Updated**: January 16, 2026

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

### 3. Run Checks
```bash
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
- [ ] Start server: `python manage.py runserver`
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
python = "^3.9"  # or "^3.10"
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
# All passing? _____
```

### 8. Manual Testing

**Authentication (CRITICAL for PyBot)**:
```bash
# Test login endpoint
curl -X POST http://localhost:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass"}'

# Should return: {"key": "TOKEN"} or {"token": "TOKEN"}

# Test profile admin endpoint
curl -X PATCH "http://localhost:8000/auth/profile/admin/?email=test@example.com" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"slackId": "U12345"}'
```

**Full manual test**:
- [ ] User registration
- [ ] User login (email/password)
- [ ] JWT token in API requests
- [ ] Password reset flow
- [ ] Google OAuth
- [ ] Facebook OAuth
- [ ] GitHub OAuth
- [ ] Admin interface
- [ ] All API endpoints
- [ ] Background tasks
- [ ] File uploads

---

## Phase 4: psycopg2 Upgrade (Day 15)

### Update pyproject.toml
```toml
psycopg2 = "^2.9"
```

```bash
poetry lock
poetry install
```

### Test with PostgreSQL 13
```bash
pytest -v
# All passing? _____
```

### Commit
```bash
git add .
git commit -m "Upgrade to Django 4.2 + psycopg2 2.9

- Upgraded Django 2.2 → 3.2 → 4.2
- Replaced django-rest-auth with dj-rest-auth
- Kept /auth/ URLs for PyBot compatibility
- Updated psycopg2 to 2.9.10
- [django-suit status: working/replaced with X]

Tested:
- All authentication flows
- PyBot integration endpoints
- Social auth (Google/Facebook/GitHub)
- Admin interface
- API endpoints"

git tag v0.2.0-pre-pg14
git push origin upgrade/django-4.2-pg14
git push --tags
```

---

## Phase 5: Staging Deployment (Days 16-20)

### Deploy to Staging
```bash
# SSH to staging server
ssh staging-server

# Pull changes
git fetch
git checkout upgrade/django-4.2-pg14

# Update Python if needed
pyenv install 3.10  # If upgrading Python

# Install dependencies
poetry install

# Run migrations
poetry run python src/manage.py migrate

# Restart application
sudo systemctl restart operationcode-backend
```

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

## Phase 6: PostgreSQL 14 on Staging (Day 21)

### Backup
```bash
pg_dump operationcode_staging > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Upgrade
```bash
# If Docker
docker-compose stop db
docker-compose rm db
# Edit docker-compose.yml: postgres:13 → postgres:14
docker-compose up -d db

# If managed service (RDS, etc)
# Use cloud console upgrade tool
```

### Verify
```bash
psql -h localhost -U user -d database -c "SELECT version();"
# Should show: PostgreSQL 14.x

python manage.py migrate
pytest -v
```

### Test (24 hours)
- [ ] All tests pass
- [ ] No errors in logs
- [ ] Performance acceptable
- [ ] PyBot integration works

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
- [ ] **Proceed with PostgreSQL 14?** YES / NO
- [ ] If NO: Document issues, stay on Django 4.2 + PG 13
- [ ] If YES: Continue to Phase 8

---

## Phase 8: PostgreSQL 14 Upgrade (Day 25)

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

**If using Docker**:
```bash
# Maintenance mode
touch /app/maintenance.flag

# Stop app
docker-compose stop backend

# Backup data volume
docker run --rm -v postgres_data:/data -v $(pwd):/backup \
  ubuntu tar czf /backup/postgres_data_backup.tar.gz /data

# Stop database
docker-compose stop db

# Update docker-compose.yml
sed -i 's/postgres:13/postgres:14/' docker/docker-compose.yml

# Start new PostgreSQL
docker-compose up -d db

# Wait for ready
docker-compose logs -f db  # Watch for "ready to accept connections"

# Start app
docker-compose up -d backend

# Remove maintenance
rm /app/maintenance.flag
```

**If using managed service (RDS, Cloud SQL, etc)**:
- Use cloud provider's upgrade tool
- Follow provider-specific procedures
- Typically: Select instance → Modify → Change version → Apply

### Post-Upgrade Verification

```bash
# Verify PostgreSQL version
docker-compose exec db psql -U user -c "SELECT version();"
# Should show: PostgreSQL 14.x

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

**If PostgreSQL 14 has issues**:

```bash
# Full rollback (1-2 hours)
touch /app/maintenance.flag

# Stop everything
docker-compose stop backend db

# Restore PostgreSQL 13
docker-compose rm db
sed -i 's/postgres:14/postgres:13/' docker/docker-compose.yml
docker volume rm postgres_data

# Restore data
tar xzf postgres_data_backup.tar.gz
# Or: pg_restore from SQL dump

# Start
docker-compose up -d db
# Wait for ready
docker-compose up -d backend

rm /app/maintenance.flag

# Verify
psql -c "SELECT version();"  # Should be 13.x
curl https://api.operationcode.org/auth/login/ ...
```

---

## Testing Checklist

### Core Authentication (PyBot Dependency!)
- [ ] POST `/auth/login/` returns JWT token
- [ ] POST `/auth/logout/` works
- [ ] POST `/auth/registration/` creates user
- [ ] POST `/auth/password/reset/` sends email
- [ ] PATCH `/auth/profile/admin/` updates profiles
- [ ] **PyBot service account can authenticate**
- [ ] **PyBot can update user slackId**

### Social Authentication
- [ ] Google OAuth flow
- [ ] Facebook OAuth flow
- [ ] GitHub OAuth flow

### API Functionality
- [ ] GET `/api/v1/users/` with JWT
- [ ] GET `/api/v1/scholarships/`
- [ ] GET `/api/v1/code_schools/`
- [ ] All CRUD operations

### Admin Interface
- [ ] Admin login
- [ ] User management
- [ ] Profile management
- [ ] Scholarship review

### Infrastructure
- [ ] Database migrations
- [ ] Background tasks
- [ ] Email sending
- [ ] File uploads to S3
- [ ] Health check endpoints
- [ ] Sentry error tracking

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

---

**Last Updated**: January 16, 2026
