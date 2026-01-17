#!/bin/bash
#
# Functional Test Script for Operation Code Backend
# Tests core functionality after deployment or upgrades
#
# Usage:
#   ./scripts/functional_test.sh              # Test localhost:8000
#   ./scripts/functional_test.sh http://api.staging.operationcode.org
#
# Prerequisites:
#   - curl
#   - python3 (for JSON parsing)
#   - Server running and accessible
#

set -e

BASE_URL="${1:-http://localhost:8000}"
PASS=0
FAIL=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Generate unique test email
TEST_EMAIL="test_$(date +%s)@example.com"
TEST_PASSWORD="TestPass123!"
ADMIN_EMAIL="admin@example.com"
ADMIN_PASSWORD="AdminPass123!"

echo "========================================"
echo "Functional Test Suite"
echo "Base URL: $BASE_URL"
echo "Test User: $TEST_EMAIL"
echo "========================================"
echo ""

# Helper function to check response
check_response() {
    local name="$1"
    local expected="$2"
    local actual="$3"

    if [[ "$actual" == *"$expected"* ]]; then
        echo -e "${GREEN}PASS${NC}: $name"
        ((PASS++))
        return 0
    else
        echo -e "${RED}FAIL${NC}: $name (expected: $expected, got: $actual)"
        ((FAIL++))
        return 1
    fi
}

# Helper function to check HTTP status
check_status() {
    local name="$1"
    local expected="$2"
    local actual="$3"

    if [[ "$actual" == "$expected" ]]; then
        echo -e "${GREEN}PASS${NC}: $name (HTTP $actual)"
        ((PASS++))
        return 0
    else
        echo -e "${RED}FAIL${NC}: $name (expected HTTP $expected, got HTTP $actual)"
        ((FAIL++))
        return 1
    fi
}

echo "--- Basic Endpoints ---"

# Health Check
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/healthz")
check_status "Health check endpoint" "200" "$STATUS"

# Admin Interface (should redirect to login)
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/admin/")
if [[ "$STATUS" == "200" || "$STATUS" == "302" ]]; then
    echo -e "${GREEN}PASS${NC}: Admin interface (HTTP $STATUS)"
    ((PASS++))
else
    echo -e "${RED}FAIL${NC}: Admin interface (expected HTTP 200 or 302, got HTTP $STATUS)"
    ((FAIL++))
fi

# API Docs
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/docs/")
check_status "API documentation" "200" "$STATUS"

echo ""
echo "--- User Registration ---"

# Register new user
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/registration/" \
    -H "Content-Type: application/json" \
    -d "{\"email\": \"$TEST_EMAIL\", \"password\": \"$TEST_PASSWORD\", \"first_name\": \"Test\", \"last_name\": \"User\"}")

if echo "$REGISTER_RESPONSE" | grep -q '"token"'; then
    echo -e "${GREEN}PASS${NC}: User registration returns JWT token"
    ((PASS++))
    TOKEN=$(echo "$REGISTER_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))" 2>/dev/null || echo "")
else
    echo -e "${RED}FAIL${NC}: User registration (response: $REGISTER_RESPONSE)"
    ((FAIL++))
    TOKEN=""
fi

echo ""
echo "--- User Login ---"

# Login
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login/" \
    -H "Content-Type: application/json" \
    -d "{\"email\": \"$TEST_EMAIL\", \"password\": \"$TEST_PASSWORD\"}")

if echo "$LOGIN_RESPONSE" | grep -q '"token"'; then
    echo -e "${GREEN}PASS${NC}: User login returns JWT token"
    ((PASS++))
    TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))" 2>/dev/null || echo "")
else
    echo -e "${RED}FAIL${NC}: User login (response: $LOGIN_RESPONSE)"
    ((FAIL++))
fi

# Test invalid login
INVALID_LOGIN=$(curl -s -X POST "$BASE_URL/auth/login/" \
    -H "Content-Type: application/json" \
    -d '{"email": "nonexistent@example.com", "password": "wrongpass"}')

if echo "$INVALID_LOGIN" | grep -q -i "incorrect\|error\|non_field_errors"; then
    echo -e "${GREEN}PASS${NC}: Invalid login rejected"
    ((PASS++))
else
    echo -e "${RED}FAIL${NC}: Invalid login should be rejected"
    ((FAIL++))
fi

echo ""
echo "--- Authenticated Endpoints ---"

if [[ -n "$TOKEN" ]]; then
    # Get profile
    PROFILE_RESPONSE=$(curl -s "$BASE_URL/auth/profile/" \
        -H "Authorization: Bearer $TOKEN")

    if echo "$PROFILE_RESPONSE" | grep -q '"id"'; then
        echo -e "${GREEN}PASS${NC}: Get profile returns user data"
        ((PASS++))
    else
        echo -e "${RED}FAIL${NC}: Get profile (response: $PROFILE_RESPONSE)"
        ((FAIL++))
    fi

    # Get user
    USER_RESPONSE=$(curl -s "$BASE_URL/auth/user/" \
        -H "Authorization: Bearer $TOKEN")

    if echo "$USER_RESPONSE" | grep -q '"email"'; then
        echo -e "${GREEN}PASS${NC}: Get user returns user data"
        ((PASS++))
    else
        echo -e "${RED}FAIL${NC}: Get user (response: $USER_RESPONSE)"
        ((FAIL++))
    fi

    # Update profile
    UPDATE_RESPONSE=$(curl -s -X PATCH "$BASE_URL/auth/profile/" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"bio": "Test bio"}')

    if echo "$UPDATE_RESPONSE" | grep -q '"bio"'; then
        echo -e "${GREEN}PASS${NC}: Update profile works"
        ((PASS++))
    else
        echo -e "${RED}FAIL${NC}: Update profile (response: $UPDATE_RESPONSE)"
        ((FAIL++))
    fi
else
    echo -e "${YELLOW}SKIP${NC}: Authenticated endpoints (no token available)"
fi

echo ""
echo "--- Password Reset ---"

RESET_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/password/reset/" \
    -H "Content-Type: application/json" \
    -d "{\"email\": \"$TEST_EMAIL\"}")

if echo "$RESET_RESPONSE" | grep -q -i "sent\|detail"; then
    echo -e "${GREEN}PASS${NC}: Password reset request accepted"
    ((PASS++))
else
    echo -e "${RED}FAIL${NC}: Password reset (response: $RESET_RESPONSE)"
    ((FAIL++))
fi

echo ""
echo "--- Admin Profile Endpoint (PyBot Integration) ---"

# Try to login as admin
ADMIN_LOGIN=$(curl -s -X POST "$BASE_URL/auth/login/" \
    -H "Content-Type: application/json" \
    -d "{\"email\": \"$ADMIN_EMAIL\", \"password\": \"$ADMIN_PASSWORD\"}" 2>/dev/null)

ADMIN_TOKEN=$(echo "$ADMIN_LOGIN" | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))" 2>/dev/null || echo "")

if [[ -n "$ADMIN_TOKEN" ]]; then
    # Test admin profile endpoint
    ADMIN_PROFILE_RESPONSE=$(curl -s -X GET "$BASE_URL/auth/profile/admin/?email=$TEST_EMAIL" \
        -H "Authorization: Bearer $ADMIN_TOKEN")

    if echo "$ADMIN_PROFILE_RESPONSE" | grep -q '"id"'; then
        echo -e "${GREEN}PASS${NC}: Admin can read user profile"
        ((PASS++))
    else
        echo -e "${RED}FAIL${NC}: Admin profile read (response: $ADMIN_PROFILE_RESPONSE)"
        ((FAIL++))
    fi

    # Test admin profile update (critical for PyBot)
    ADMIN_UPDATE_RESPONSE=$(curl -s -X PATCH "$BASE_URL/auth/profile/admin/?email=$TEST_EMAIL" \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"slackId": "U_FUNC_TEST"}')

    if echo "$ADMIN_UPDATE_RESPONSE" | grep -q '"slackId".*"U_FUNC_TEST"'; then
        echo -e "${GREEN}PASS${NC}: Admin can update slackId (PyBot critical)"
        ((PASS++))
    else
        echo -e "${RED}FAIL${NC}: Admin profile update (response: $ADMIN_UPDATE_RESPONSE)"
        ((FAIL++))
    fi
else
    echo -e "${YELLOW}SKIP${NC}: Admin profile endpoint tests (admin user not available)"
    echo "       To test, create admin user with ProfileAdmin group:"
    echo "       docker compose exec backend python manage.py shell"
    echo "       >>> from django.contrib.auth.models import User, Group"
    echo "       >>> group, _ = Group.objects.get_or_create(name='ProfileAdmin')"
    echo "       >>> user = User.objects.create_user('admin@example.com', 'admin@example.com', 'AdminPass123!', is_staff=True)"
    echo "       >>> user.groups.add(group)"
fi

echo ""
echo "--- Unauthenticated Access Control ---"

# Test that profile requires auth
UNAUTH_PROFILE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/auth/profile/")
if [[ "$UNAUTH_PROFILE" == "401" || "$UNAUTH_PROFILE" == "403" ]]; then
    echo -e "${GREEN}PASS${NC}: Profile endpoint requires authentication (HTTP $UNAUTH_PROFILE)"
    ((PASS++))
else
    echo -e "${RED}FAIL${NC}: Profile should require auth (got HTTP $UNAUTH_PROFILE)"
    ((FAIL++))
fi

# Test that admin endpoint requires auth
UNAUTH_ADMIN=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/auth/profile/admin/?email=test@example.com")
if [[ "$UNAUTH_ADMIN" == "401" || "$UNAUTH_ADMIN" == "403" ]]; then
    echo -e "${GREEN}PASS${NC}: Admin profile endpoint requires authentication (HTTP $UNAUTH_ADMIN)"
    ((PASS++))
else
    echo -e "${RED}FAIL${NC}: Admin profile should require auth (got HTTP $UNAUTH_ADMIN)"
    ((FAIL++))
fi

echo ""
echo "========================================"
echo "Results: ${GREEN}$PASS passed${NC}, ${RED}$FAIL failed${NC}"
echo "========================================"

if [[ $FAIL -gt 0 ]]; then
    exit 1
else
    exit 0
fi
