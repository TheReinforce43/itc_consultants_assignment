# ITC Consultants Assignment

A Django REST Framework backend implementing JWT-based authentication (Signup, Login, Logout, Token Refresh) and a role-based Task management API, fully dockerized with Nginx, PostgreSQL, automated tests, and CI.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Authentication Flow](#authentication-flow)
  - [1. Signup](#1-signup)
  - [2. Login](#2-login)
  - [3. Logout](#3-logout)
  - [4. Token Refresh](#4-token-refresh)
- [Role-Based Access Control (RBAC)](#role-based-access-control-rbac)
- [Attribute-Based Access Control (ABAC)](#attribute-based-access-control-abac)
- [API Endpoints](#api-endpoints)
- [Setup & Installation](#setup--installation)
- [Environment Variables](#environment-variables)
- [Running with Docker](#running-with-docker)
- [Running Migrations](#running-migrations)
- [Running Tests](#running-tests)
- [CI/CD (GitHub Actions)](#cicd-github-actions)
- [Rate Limiting](#rate-limiting)
- [CORS & Allowed Hosts](#cors--allowed-hosts)
- [Error Handling / Edge Cases](#error-handling--edge-cases)

---

## Features

- User signup with model-level validation
- JWT-based login and logout (with token blacklisting)
- Automatic access token renewal via refresh token
- Role-Based Access Control (RBAC) — Admin / Seller / Customer / Staff
- Attribute-Based Access Control (ABAC) — time-based write restriction (no create/update/delete after 6 PM)
- Task CRUD API with per-role, per-time-window permissions
- Request throttling (rate limiting) for both anonymous and authenticated users
- CORS configuration for frontend integration
- Environment-based `ALLOWED_HOSTS` (dev vs production)
- Dockerized setup with Nginx reverse proxy and PostgreSQL
- Unit testing with `pytest`
- GitHub Actions CI pipeline for automated testing

---

## Tech Stack

| Layer          | Technology                          |
|----------------|--------------------------------------|
| Language       | Python 3.12                          |
| Framework      | Django + Django REST Framework       |
| Auth           | `djangorestframework-simplejwt`      |
| Database       | PostgreSQL 16                        |
| Web Server     | Gunicorn                             |
| Reverse Proxy  | Nginx                                |
| Testing        | Pytest                               |
| CI/CD          | GitHub Actions                       |
| Containerization | Docker & Docker Compose            |

---

## Project Structure

```
itc_consultants_assignment/
├── user/
│   ├── View/
│   │   └── user_view.py        # Signup, Login, Logout, Refresh Token views
│   ├── models.py                # Custom User model (roles: Admin, Seller, Customer)
│   ├── urls.py
│   └── migrations/
├── task/
│   ├── View/
│   │   └── task_view.py        # TaskViewSet (ModelViewSet)
│   ├── permissions.py          # TaskPermission (RBAC logic)
│   ├── models.py                # TaskModel
│   ├── urls.py                  # DRF DefaultRouter
│   └── migrations/
├── nginx/
│   └── nginx.conf
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── manage.py
```

---

## Authentication Flow

### 1. Signup

**Endpoint:** `POST /user/signup/`

Order of validation on every signup request:

1. **Rate limiting** — Anonymous users are throttled (see [Rate Limiting](#rate-limiting)). Exceeding the limit returns `429 Too Many Requests`.
2. **CORS check** — Only requests originating from an allowed origin (`CORS_ALLOWED_ORIGINS`) are accepted by the browser; other origins are blocked at the browser level.
3. **Allowed hosts check** — The `Host` header must match `ALLOWED_HOSTS`, or Django returns a `400 Bad Request` (`DisallowedHost`).
4. **Model / serializer validation** — Email format, password strength, uniqueness of email, and required fields are validated. Invalid input returns `400 Bad Request` with field-level error messages.

If all checks pass, a new `User` record is created and the user can proceed to log in.

**Sample Request:**
```json
POST /user/signup/
{
  "email": "john@example.com",
  "password": "StrongPass123!",
  "roles": "Customer"
}
```

**Sample Success Response (201):**
```json
{
  "email": "john@example.com",
  "roles": "Customer"
}
```

**Sample Failure Responses:**
```json
// 400 - Validation error
{
  "email": ["User with this email already exists."]
}
```
```json
// 429 - Rate limit exceeded
{
  "detail": "Request was throttled. Expected available in 42 seconds."
}
```

---

### 2. Login

**Endpoint:** `POST /user/login/`

Validation order:

1. Check that the account with the given **email** exists.
2. Verify the **password** against the stored hash.
3. If either check fails, return a generic `401 Unauthorized` (avoid leaking whether the email or password was wrong, to prevent user enumeration).
4. On success, issue a JWT **access token** and **refresh token**.

**Sample Request:**
```json
POST /user/login/
{
  "email": "john@example.com",
  "password": "StrongPass123!"
}
```

**Sample Success Response (200):**
```json
{
  "access": "eyJhbGciOi...",
  "refresh": "eyJhbGciOi..."
}
```

**Sample Failure Response (401):**
```json
{
  "detail": "Invalid email or password."
}
```

---

### 3. Logout

**Endpoint:** `POST /user/logout/`

- Requires a valid **access token** in the `Authorization` header.
- Accepts the user's **refresh token** in the request body.
- The refresh token is **blacklisted**, so it can no longer be used to generate new access tokens — effectively ending the session.

**Sample Request:**
```
POST /user/logout/
Authorization: Bearer <access_token>

{
  "refresh": "eyJhbGciOi..."
}
```

**Sample Success Response (200):**
```json
{
  "detail": "Successfully logged out."
}
```

**Sample Failure Response (400):**
```json
{
  "detail": "Token is invalid or already blacklisted."
}
```

> **Note:** Token blacklisting requires `rest_framework_simplejwt.token_blacklist` to be added to `INSTALLED_APPS`, with its migrations applied.

---

### 4. Token Refresh

**Endpoint:** `POST /user/refresh-token/`

- When the **access token expires**, the client sends the **refresh token** to this endpoint.
- If the refresh token is valid (not expired, not blacklisted), a new access token is issued.
- If the refresh token is also expired or blacklisted, the user must log in again.

**Sample Request:**
```json
POST /user/refresh-token/
{
  "refresh": "eyJhbGciOi..."
}
```

**Sample Success Response (200):**
```json
{
  "access": "eyJhbGciOi..."
}
```

**Sample Failure Response (401):**
```json
{
  "detail": "Token is invalid or expired.",
  "code": "token_not_valid"
}
```

**Frontend integration tip:** Use an HTTP interceptor (Axios/Fetch) that detects a `401` on any API call, automatically calls `/refresh-token/`, retries the original request with the new access token, and redirects to login only if the refresh also fails.

---

## Role-Based Access Control (RBAC)

Roles are defined on the `User` model:

```python
user_roles = (
    ('Admin', 'Admin'),
    ('Seller', 'Seller'),
    ('Customer', 'Customer'),
)
```

Permissions are enforced in `TaskPermission` (`task/permissions.py`):

| Role       | GET / List | POST (Create) | PUT / PATCH (Update) | DELETE |
|------------|:----------:|:--------------:|:---------------------:|:------:|
| **Admin (superuser)** | ✅ | ✅ | ✅ | ✅ |
| **Staff**  | ✅ | ✅ | ✅ | ❌ |
| **Customer** | ✅ | ❌ | ❌ | ❌ |
| **Seller** | ❌ (not currently handled — see note below) | ❌ | ❌ | ❌ |
| **Unauthenticated** | ❌ | ❌ | ❌ | ❌ |

> ⚠️ **Known inconsistency to review:** `user_roles` defines `Admin`, `Seller`, `Customer`, but `TaskPermission` checks for `"Customer"` and `"Staff"` — `"Staff"` and `"Seller"` do not match. Confirm whether `"Staff"` should be renamed to `"Seller"` in either the model choices or the permission class so Seller accounts get the intended access instead of falling through to `return False`.

---

## Attribute-Based Access Control (ABAC)

In addition to role (RBAC), access is also gated by a **contextual attribute — the current time**. This layer applies uniformly, on top of RBAC, regardless of role:

> **After 6:00 PM (18:00, server local time), no user — including Admin — may create, update, or delete a task. Read access (`GET`/`HEAD`/`OPTIONS`) remains available at all times.**

This is enforced as the *first* check inside `TaskPermission.has_permission()`, before any role-based branching, so it uniformly overrides every role's write access once the time window is hit:

```python
from django.utils import timezone
from rest_framework.permissions import BasePermission


class TaskPermission(BasePermission):

    WRITE_METHODS = ["POST", "PUT", "PATCH", "DELETE"]

    def has_permission(self, request, view):

        if not request.user or not request.user.is_authenticated:
            return False

        # ABAC: block all writes after 6 PM, regardless of role
        current_hour = timezone.localtime(timezone.now()).hour
        if current_hour >= 18 and request.method in self.WRITE_METHODS:
            return False

        if request.user.is_superuser:
            return True

        if request.user.roles == "Customer":
            return request.method in ["GET", "HEAD", "OPTIONS"]

        if request.user.roles == "Staff":
            return request.method in [
                "GET", "HEAD", "OPTIONS", "POST", "PUT", "PATCH",
            ]

        return False
```

| Time window | Read (`GET`) | Write (`POST`/`PUT`/`PATCH`/`DELETE`) |
|-------------|:-------------:|:----------------------------------------:|
| Before 6 PM | ✅ (per role) | ✅ (per role, see RBAC table above) |
| 6 PM onward | ✅ (per role) | ❌ for **everyone**, including Admin |

**Design notes:**
- Uses `timezone.localtime(timezone.now())` (not raw `datetime.now()`) so the check respects Django's `TIME_ZONE` setting rather than the container's system clock, which is UTC by default in Docker.
- This is a genuine ABAC example (decision based on a runtime *attribute* — time of request — rather than a static *role*), layered on top of the existing RBAC checks.
- If Admin should be **exempt** from the time restriction (business rule TBD), move the time-gate check to *after* the `is_superuser` branch instead of before it.

**Testing note:** since this depends on wall-clock time, tests should mock `django.utils.timezone.now` (via `unittest.mock.patch`) rather than relying on when the suite happens to run — see `task/tests/test_abac_permissions.py`.

---

## API Endpoints

| Method | Endpoint | Auth Required | Description |
|--------|----------|:--------------:|--------------|
| POST | `/user/signup/` | No | Register a new user |
| POST | `/user/login/` | No | Obtain access & refresh tokens |
| POST | `/user/logout/` | Yes | Blacklist refresh token |
| POST | `/user/refresh-token/` | No (refresh token in body) | Get new access token |
| GET | `/task/tasks/` | Yes | List tasks (blocked nowhere; time-agnostic) |
| POST | `/task/tasks/` | Yes (Admin/Staff, **before 6 PM only**) | Create a task |
| GET | `/task/tasks/{id}/` | Yes | Retrieve a task |
| PUT/PATCH | `/task/tasks/{id}/` | Yes (Admin/Staff, **before 6 PM only**) | Update a task |
| DELETE | `/task/tasks/{id}/` | Yes (Admin only, **before 6 PM only**) | Delete a task |

> Base path (`/user/`, `/task/`) matches the prefixes registered in the project's root `urls.py` (`path("user/", include("user.urls"))`, `path("task/", include("task.urls"))`).

---

## Setup & Installation

### Prerequisites
- Docker & Docker Compose
- (Optional, for local dev without Docker) Python 3.12, PostgreSQL 16

### Clone the repository
```bash
git clone <repo-url>
cd itc_consultants_assignment
```

### Create environment file
```bash
cp .env.example .env
```
Fill in the values as described in [Environment Variables](#environment-variables).

---

## Environment Variables

Create a `.env` file in the project root:

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=1

# Database
DB_NAME=itc_db
DB_USER=itc_user
DB_PASSWORD=itc_password
DB_HOST=db
DB_PORT=5432
```

| Variable | Description |
|----------|--------------|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `1` for development (allows all hosts), `0` for production |
| `DB_NAME` / `DB_USER` / `DB_PASSWORD` | PostgreSQL credentials |
| `DB_HOST` | Set to `db` (the Docker Compose service name) |
| `DB_PORT` | Default `5432` |

---

## Running with Docker

Build and start all services (`db`, `web`, `nginx`):

```bash
docker compose up -d --build
```

Check that all containers are running:
```bash
docker compose ps
```

The API will be available through Nginx at:
```
http://localhost/
```

> Note: `web` (gunicorn) only listens internally on port `8000` and is **not** published to the host directly — all traffic goes through Nginx on port `80`.

Stop all services:
```bash
docker compose down
```

---

## Running Migrations

Whenever models change:

```bash
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
```

> If a container is crash-looping and `exec` fails, use `docker compose run --rm web python manage.py makemigrations` instead — it spins up a fresh container so you can still generate migrations, which will persist to your host via the project's bind mount (`.:/app`).

---

## Running Tests

Unit tests are written with `pytest` (via `pytest-django`).

```bash
docker compose exec web pytest
```

Run with coverage:
```bash
docker compose exec web pytest --cov=.
```

Run a specific test file:
```bash
docker compose exec web pytest task/tests/test_views.py
```

Suggested test coverage:
- Signup: valid data, duplicate email, weak password, missing fields, rate limit exceeded
- Login: correct credentials, wrong password, non-existent email
- Logout: valid token blacklisted, already-blacklisted token, missing token
- Refresh: valid refresh token, expired refresh token, blacklisted refresh token
- Task RBAC: each role (Admin/Staff/Customer) against each HTTP method (`task/tests/test_views.py`)
- Task ABAC: write operations blocked at/after 6 PM for every role, reads unaffected, mocking `django.utils.timezone.now` rather than relying on wall-clock time (`task/tests/test_abac_permissions.py`)

---

## CI/CD (GitHub Actions)

A workflow (e.g. `.github/workflows/ci.yml`) runs the test suite automatically on every push / pull request:

```yaml
name: CI

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: itc_db
          POSTGRES_USER: itc_user
          POSTGRES_PASSWORD: itc_password
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 5s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run migrations
        env:
          DB_NAME: itc_db
          DB_USER: itc_user
          DB_PASSWORD: itc_password
          DB_HOST: localhost
          DB_PORT: 5432
        run: |
          python manage.py migrate

      - name: Run tests
        env:
          DB_NAME: itc_db
          DB_USER: itc_user
          DB_PASSWORD: itc_password
          DB_HOST: localhost
          DB_PORT: 5432
        run: |
          pytest
```

> Adjust environment variable names to match whatever your `settings.py` actually reads.

---

## Rate Limiting

Configured globally in `settings.py`:

```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '5/minute',
        'user': '30/minute',
    }
}
```

- **Anonymous users** (e.g. calling `/signup/` or `/login/`): max **5 requests/minute**.
- **Authenticated users**: max **30 requests/minute**.
- Exceeding the limit returns `429 Too Many Requests` with a `Retry-After`-style message.

---

## CORS & Allowed Hosts

```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',  # frontend dev URL
]
```
- Only origins in this list can make cross-origin requests (e.g. from a React/Next.js frontend running on port 3000).
- Add your production frontend domain here before deploying.

```python
if DEBUG:
    ALLOWED_HOSTS = ["*", "127.0.0.1", "localhost"]
else:
    ALLOWED_HOSTS = [
        # production domain(s) go here, e.g. "api.yourdomain.com"
    ]
```
- In development (`DEBUG=1`), all hosts are allowed for convenience.
- In production (`DEBUG=0`), **you must explicitly list your domain(s)** — an empty list will cause every request to fail with `400 Bad Request` (`DisallowedHost`), so this must be filled in before deploying.

---

## Error Handling / Edge Cases

| Scenario | Expected Behavior |
|----------|--------------------|
| Signup with existing email | `400` with field error |
| Signup rate limit exceeded | `429` |
| Signup with invalid/mismatched Host header | `400 DisallowedHost` |
| Login with wrong password | `401` generic error (no user enumeration) |
| Login with non-existent email | `401` generic error (same message as wrong password) |
| Logout without access token | `401 Unauthorized` |
| Logout with already-blacklisted refresh token | `400` token invalid |
| Refresh with expired refresh token | `401`, client should force re-login |
| Refresh with blacklisted refresh token | `401 token_not_valid` |
| Task create/update/delete by Customer | `403 Forbidden` |
| Task delete by Staff | `403 Forbidden` (only Admin can delete) |
| Any Task endpoint without auth | `401 Unauthorized` |
| Task create/update/delete by **any role, at/after 6 PM** | `403 Forbidden` (ABAC time-gate; read still allowed) |
| CORS request from disallowed origin | Blocked by browser (no `Access-Control-Allow-Origin` header) |

---
