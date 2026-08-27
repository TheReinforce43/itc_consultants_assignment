# Django REST Framework Project

A production-ready Django REST Framework (DRF) API with JWT authentication, Docker containerization, NGINX reverse proxy, Redis caching, comprehensive testing, rate limiting, email notifications, stored procedures, and Swagger API documentation.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Environment Configuration](#environment-configuration)
- [Running the Application](#running-the-application)
- [Docker Deployment](#docker-deployment)
- [API Documentation](#api-documentation)
- [Authentication (JWT)](#authentication-jwt)
- [Rate Limiting](#rate-limiting)
- [Email Configuration](#email-configuration)
- [Using Stored Procedures](#using-stored-procedures)
- [Testing](#testing)
- [Caching with Redis](#caching-with-redis)
- [Monitoring & Logs](#monitoring--logs)
- [Troubleshooting](#troubleshooting)

---

## Features

✅ **JWT Authentication** - Secure token-based authentication  
✅ **Docker & Docker Compose** - Containerized development and production  
✅ **NGINX** - Reverse proxy and load balancing  
✅ **Redis** - Caching and rate limiting backend  
✅ **Pytest** - Comprehensive testing suite with AAA pattern  
✅ **Rate Limiting/Throttling** - Per-user and anonymous rate limits  
✅ **Email Notifications** - Async email sending on signup  
✅ **Stored Procedures** - Database-level logic instead of ORM  
✅ **Swagger/OpenAPI** - Interactive API documentation  
✅ **PostgreSQL** - Robust relational database  
✅ **Celery** - Async task queue for email and background jobs  

---

## Prerequisites

- Python 3.10+
- PostgreSQL 13+
- Redis 7+
- Docker & Docker Compose
- Git

---

## Project Structure

```
project_root/
├── manage.py
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── nginx.conf
├── pytest.ini
├── .env.example
├── .gitignore
│
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   ├── prod.py
│   │   └── __init__.py
│   ├── urls.py
│   ├── wsgi.py
│   └── celery.py
│
├── apps/
│   ├── users/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── tasks.py
│   │   └── tests/
│   │       ├── test_models.py
│   │       ├── test_views.py
│   │       └── test_serializers.py
│   │
│   ├── products/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests/
│   │
│   └── orders/
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       ├── urls.py
│       └── tests/
│
├── utils/
│   ├── db.py (stored procedures)
│   ├── decorators.py
│   └── exceptions.py
│
└── docker/
    ├── Dockerfile
    ├── docker-compose.yml
    └── nginx.conf
```

---

## Installation & Setup

### 1. Clone and Setup Virtual Environment

```bash
git clone <repository-url>
cd project_root

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Install Required Packages

```bash
# requirements.txt should contain:
Django==4.2.0
djangorestframework==3.14.0
djangorestframework-simplejwt==5.2.2
django-redis==5.2.0
psycopg2-binary==2.9.6
celery==5.3.0
drf-spectacular==0.26.1
pytest==7.3.1
pytest-django==4.5.2
pytest-cov==4.1.0
django-cors-headers==4.0.0
python-decouple==3.8
```

Install all:
```bash
pip install -r requirements.txt
```

### 3. Create Environment File

```bash
cp .env.example .env
```

Edit `.env` with your configuration (see [Environment Configuration](#environment-configuration))

### 4. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load initial data (if needed)
python manage.py loaddata fixtures/initial_data.json
```

---

## Environment Configuration

Create `.env` file in project root:

```env
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=drf_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0
CACHE_REDIS_URL=redis://localhost:6379/1

# JWT
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Rate Limiting
RATE_LIMIT_ANON=5/minute
RATE_LIMIT_USER=30/minute

# AWS (if using S3)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
```

---

## Running the Application

### Development (Without Docker)

```bash
# Start PostgreSQL
sudo service postgresql start

# Start Redis
redis-server

# Start Celery worker (in separate terminal)
celery -A config worker -l info

# Start Celery beat scheduler (in separate terminal)
celery -A config beat -l info

# Run development server
python manage.py runserver
```

Visit: `http://localhost:8000`

### Development (With Docker)

See [Docker Deployment](#docker-deployment) section

---

## Docker Deployment

### Prerequisites

- Docker installed
- Docker Compose installed

### Directory Structure for Docker

```
docker/
├── Dockerfile
├── docker-compose.yml
├── docker-compose.prod.yml
└── nginx.conf
```

### docker-compose.yml (Development)

```yaml
version: '3.9'

services:
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  web:
    build: .
    command: |
      sh -c "python manage.py migrate &&
             python manage.py collectstatic --noinput &&
             gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4"
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
    ports:
      - "8000:8000"
    environment:
      - DEBUG=${DEBUG}
      - SECRET_KEY=${SECRET_KEY}
      - DB_HOST=db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

  celery:
    build: .
    command: celery -A config worker -l info
    volumes:
      - .:/app
    environment:
      - DEBUG=${DEBUG}
      - DB_HOST=db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
      - web

  celery-beat:
    build: .
    command: celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    volumes:
      - .:/app
    environment:
      - DEBUG=${DEBUG}
      - DB_HOST=db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
      - web

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - static_volume:/app/staticfiles:ro
    ports:
      - "80:80"
    depends_on:
      - web

volumes:
  postgres_data:
  static_volume:
```

### Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### NGINX Configuration (nginx.conf)

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    # Rate limiting zones
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=5r/m;
    limit_req_zone $http_x_forwarded_for zone=user_limit:10m rate=30r/m;

    upstream django_app {
        server web:8000;
    }

    server {
        listen 80;
        server_name _;

        # Static files
        location /static/ {
            alias /app/staticfiles/;
        }

        # API with rate limiting
        location /api/ {
            limit_req zone=api_limit burst=10 nodelay;
            
            proxy_pass http://django_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 30s;
        }

        # Swagger docs
        location /api/docs/ {
            proxy_pass http://django_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # Health check
        location /health/ {
            proxy_pass http://django_app;
            access_log off;
        }

        # Redirect root to API docs
        location / {
            return 301 /api/docs/;
        }
    }
}
```

### Run with Docker Compose

```bash
# Development
docker-compose up -d

# View logs
docker-compose logs -f web

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Shutdown
docker-compose down
```

---

## API Documentation

### Swagger/OpenAPI Setup

**1. Install package:**
```bash
pip install drf-spectacular
```

**2. Update settings.py:**

```python
INSTALLED_APPS = [
    # ...
    'drf_spectacular',
    'rest_framework',
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Your API',
    'DESCRIPTION': 'API Documentation',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': r'/api/',
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorizationData': True,
        'displayOperationId': False,
    },
}
```

**3. Update urls.py:**

```python
from drf_spectacular.views import SpectacularSwaggerView, SpectacularRetrieveAPIView

urlpatterns = [
    path('api/schema/', SpectacularRetrieveAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
```

**4. Access Swagger UI:**
```
http://localhost:8000/api/docs/
```

---

## Authentication (JWT)

### 1. JWT Configuration

**settings.py:**
```python
INSTALLED_APPS = [
    'rest_framework_simplejwt',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
}
```

### 2. User Authentication Views

**apps/users/views.py:**
```python
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer
from .models import User
from .tasks import send_welcome_email

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """User registration with email verification"""
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # Send welcome email asynchronously
        send_welcome_email.delay(user.id)
        return Response(
            {'message': 'User created. Check email for verification.'},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

### 3. Using JWT in Requests

```bash
# Get tokens
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass"}'

# Use access token
curl -H "Authorization: Bearer <access_token>" \
  http://localhost:8000/api/protected-endpoint/

# Refresh token
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"<refresh_token>"}'
```

---

## Rate Limiting

### Configuration

**settings.py:**
```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '5/minute',      # 5 hits per minute for anonymous
        'user': '30/minute'      # 30 hits per minute for authenticated
    }
}

# Cache settings for throttling
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### Custom Throttles

**utils/throttles.py:**
```python
from rest_framework.throttling import SimpleRateThrottle

class UnauthenticatedThrottle(SimpleRateThrottle):
    scope = 'unauthenticated'
    
    def get_cache_key(self):
        if self.request.user and self.request.user.is_authenticated:
            return None
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(self.request)
        }

class LoginThrottle(SimpleRateThrottle):
    """Strict rate limit for login attempts"""
    scope = 'login'
    
    def get_cache_key(self):
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(self.request)
        }
```

### Apply to Views

```python
from rest_framework.decorators import throttle_classes
from utils.throttles import LoginThrottle

@throttle_classes([LoginThrottle])
class LoginView(APIView):
    def post(self, request):
        # Login logic
        pass
```

---

## Email Configuration

### 1. Environment Setup

Add to `.env`:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 2. Settings Configuration

**config/settings/base.py:**
```python
import os

EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND',
    'django.core.mail.backends.smtp.EmailBackend'
)
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', True)
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```

### 3. Celery Task for Email

**apps/users/tasks.py:**
```python
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import User

@shared_task
def send_welcome_email(user_id):
    """Send welcome email to newly registered user"""
    try:
        user = User.objects.get(id=user_id)
        
        context = {
            'username': user.username,
            'email': user.email,
        }
        
        html_message = render_to_string('emails/welcome.html', context)
        
        send_mail(
            subject='Welcome to Our Platform',
            message=f'Welcome {user.username}!',
            from_email='noreply@example.com',
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        print(f"Welcome email sent to {user.email}")
    except User.DoesNotExist:
        print(f"User {user_id} not found")
    except Exception as e:
        print(f"Error sending email: {str(e)}")

@shared_task
def send_password_reset_email(user_id, reset_token):
    """Send password reset email"""
    try:
        user = User.objects.get(id=user_id)
        reset_link = f"https://yoursite.com/reset-password/{reset_token}/"
        
        send_mail(
            subject='Password Reset Request',
            message=f'Reset your password here: {reset_link}',
            from_email='noreply@example.com',
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error sending reset email: {str(e)}")
```

### 4. Email Template

**templates/emails/welcome.html:**
```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; }
        .container { max-width: 600px; margin: 0 auto; }
        .header { background-color: #007bff; color: white; padding: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to Our Platform!</h1>
        </div>
        <p>Hi {{ username }},</p>
        <p>Thank you for signing up. Your account has been created successfully.</p>
        <p>Email: {{ email }}</p>
        <p>Best regards,<br>The Team</p>
    </div>
</body>
</html>
```

### 5. Trigger Email on Signup

**apps/users/views.py:**
```python
from .tasks import send_welcome_email

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # Send async email
        send_welcome_email.delay(user.id)
        return Response(
            {'message': 'User created. Check email.'},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

---

## Using Stored Procedures

### 1. Create Stored Procedure in PostgreSQL

```sql
-- Create function/procedure in PostgreSQL
CREATE OR REPLACE FUNCTION calculate_order_total(p_order_id INTEGER)
RETURNS TABLE (
    order_id INTEGER,
    total_amount DECIMAL,
    tax DECIMAL,
    final_price DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        o.id,
        o.total_amount,
        o.tax,
        (o.total_amount + o.tax) as final_price
    FROM orders o
    WHERE o.id = p_order_id;
END;
$$ LANGUAGE plpgsql;
```

### 2. Utility Function for Stored Procedures

**utils/db.py:**
```python
from django.db import connection

def call_stored_procedure(proc_name, params=None):
    """
    Universal helper to call stored procedures/functions
    
    Args:
        proc_name: Name of stored procedure/function
        params: List of parameters
    
    Returns:
        Tuple (results, error)
    """
    try:
        with connection.cursor() as cursor:
            if params:
                placeholders = ','.join(['%s'] * len(params))
                cursor.execute(
                    f'SELECT * FROM {proc_name}({placeholders})',
                    params
                )
            else:
                cursor.execute(f'SELECT * FROM {proc_name}()')
            
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return results, None
    except Exception as e:
        return None, str(e)

def execute_stored_procedure(proc_name, params=None):
    """Execute stored procedure that modifies data (INSERT/UPDATE/DELETE)"""
    try:
        with connection.cursor() as cursor:
            if params:
                placeholders = ','.join(['%s'] * len(params))
                cursor.callproc(proc_name, params)
            else:
                cursor.callproc(proc_name, [])
        return True, None
    except Exception as e:
        return False, str(e)
```

### 3. Use in Views

**apps/orders/views.py:**
```python
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets
from utils.db import call_stored_procedure, execute_stored_procedure
from .models import Order
from .serializers import OrderSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    @action(detail=True, methods=['get'])
    def calculate_total(self, request, pk=None):
        """Call stored procedure to calculate order total"""
        results, error = call_stored_procedure('calculate_order_total', [pk])
        
        if error:
            return Response(
                {'error': error},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        if not results:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(results[0])
    
    @action(detail=True, methods=['post'])
    def apply_discount(self, request, pk=None):
        """Call procedure to apply discount"""
        discount = request.data.get('discount')
        
        success, error = execute_stored_procedure(
            'apply_order_discount',
            [pk, discount]
        )
        
        if not success:
            return Response(
                {'error': error},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response({'status': 'Discount applied'})
```

### 4. Run Stored Procedures with Django Management Command

**apps/orders/management/commands/init_procedures.py:**
```python
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Initialize database stored procedures'
    
    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Read SQL file
            with open('apps/orders/sql/procedures.sql', 'r') as f:
                sql = f.read()
            
            cursor.execute(sql)
        
        self.stdout.write(
            self.style.SUCCESS('Stored procedures created successfully')
        )
```

Run:
```bash
python manage.py init_procedures
```

---

## Testing

### 1. Pytest Configuration

**pytest.ini:**
```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.test
python_files = tests.py test_*.py *_tests.py
python_classes = Test*
python_functions = test_*
addopts = --cov=apps --cov-report=html --cov-report=term-missing -v
testpaths = apps
```

**config/settings/test.py:**
```python
from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES = True

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

DEBUG = True
```

### 2. Test Structure (AAA Pattern)

**apps/users/tests/test_views.py:**
```python
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

@pytest.mark.django_db
class TestUserSignUp:
    
    def setup_method(self):
        """Setup for each test"""
        self.client = APIClient()
        self.signup_url = '/api/users/signup/'
    
    def test_user_signup_success(self):
        # Arrange
        payload = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password2': 'testpass123',
        }
        
        # Act
        response = self.client.post(self.signup_url, payload)
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username='testuser').exists()
    
    def test_user_signup_invalid_email(self):
        # Arrange
        payload = {
            'username': 'testuser',
            'email': 'invalid-email',
            'password': 'testpass123',
            'password2': 'testpass123',
        }
        
        # Act
        response = self.client.post(self.signup_url, payload)
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data
    
    def test_user_signup_password_mismatch(self):
        # Arrange
        payload = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password2': 'different',
        }
        
        # Act
        response = self.client.post(self.signup_url, payload)
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
class TestUserLogin:
    
    def setup_method(self):
        self.client = APIClient()
        self.login_url = '/api/token/'
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
    
    def test_login_success(self):
        # Arrange
        payload = {
            'username': 'testuser',
            'password': 'testpass123',
        }
        
        # Act
        response = self.client.post(self.login_url, payload)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
    
    def test_login_invalid_credentials(self):
        # Arrange
        payload = {
            'username': 'testuser',
            'password': 'wrongpassword',
        }
        
        # Act
        response = self.client.post(self.login_url, payload)
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
```

### 3. Run Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest apps/users/tests/test_views.py

# Run specific test class
pytest apps/users/tests/test_views.py::TestUserSignUp

# Run specific test with verbose output
pytest -v apps/users/tests/test_views.py::TestUserSignUp::test_user_signup_success

# Run with coverage report
pytest --cov=apps --cov-report=html

# Run tests in parallel
pytest -n auto
```

---

## Caching with Redis

### 1. Redis Configuration

**settings.py:**
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'IGNORE_EXCEPTIONS': True,
        }
    }
}

# Cache timeout (1 hour)
CACHE_TTL = 60 * 60
```

### 2. Cache in Views

**apps/products/views.py:**
```python
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Cache for 1 hour
@cache_page(60 * 60)
@api_view(['GET'])
def get_products(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

# Manual cache control
@api_view(['GET'])
def get_product_detail(request, pk):
    cache_key = f'product_{pk}'
    
    # Try to get from cache
    product_data = cache.get(cache_key)
    
    if product_data is None:
        product = Product.objects.get(pk=pk)
        serializer = ProductSerializer(product)
        product_data = serializer.data
        # Cache for 1 hour
        cache.set(cache_key, product_data, 60 * 60)
    
    return Response(product_data)

# Invalidate cache on update
@api_view(['PUT'])
def update_product(request, pk):
    product = Product.objects.get(pk=pk)
    serializer = ProductSerializer(product, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        # Clear cache
        cache.delete(f'product_{pk}')
        return Response(serializer.data)
    
    return Response(serializer.errors, status=400)
```

### 3. Cache Decorator Utility

**utils/decorators.py:**
```python
from functools import wraps
from django.core.cache import cache

def cache_result(timeout=3600):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}_{str(args)}_{str(kwargs)}"
            result = cache.get(cache_key)
            
            if result is None:
                result = func(*args, **kwargs)
                cache.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator

# Usage
@cache_result(timeout=60*60)
def get_expensive_calculation():
    return expensive_operation()
```

---

## Monitoring & Logs

### 1. Logging Configuration

**settings.py:**
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/django.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'celery': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
    },
}
```

### 2. Application Logging

**apps/users/views.py:**
```python
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
def signup(request):
    logger.info(f"New signup attempt from {request.META.get('REMOTE_ADDR')}")
    
    try:
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            logger.info(f"User {user.id} created successfully")
            send_welcome_email.delay(user.id)
            return Response({'message': 'Success'}, status=201)
        else:
            logger.warning(f"Signup validation failed: {serializer.errors}")
            return Response(serializer.errors, status=400)
    except Exception as e:
        logger.error(f"Signup error: {str(e)}", exc_info=True)
        return Response({'error': 'Server error'}, status=500)
```

### 3. Health Check Endpoint

**config/urls.py:**
```python
from django.http import JsonResponse

def health_check(request):
    """Health check endpoint for monitoring"""
    from django.db import connection
    from django_redis import get_redis_connection
    
    status = {'status': 'ok', 'checks': {}}
    
    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        status['checks']['database'] = 'ok'
    except Exception as e:
        status['status'] = 'error'
        status['checks']['database'] = str(e)
    
    # Check Redis
    try:
        redis_conn = get_redis_connection('default')
        redis_conn.ping()
        status['checks']['redis'] = 'ok'
    except Exception as e:
        status['status'] = 'error'
        status['checks']['redis'] = str(e)
    
    status_code = 200 if status['status'] == 'ok' else 503
    return JsonResponse(status, status=status_code)

urlpatterns = [
    path('health/', health_check),
]
```

---

## Troubleshooting

### PostgreSQL Connection Issues

```bash
# Check if PostgreSQL is running
sudo service postgresql status

# Check connection
psql -U postgres -d drf_db -c "SELECT 1"

# Docker: Check logs
docker-compose logs db
```

### Redis Connection Issues

```bash
# Check if Redis is running
redis-cli ping

# Docker: Check logs
docker-compose logs redis

# Check Redis connection
redis-cli -u redis://localhost:6379
```

### Celery Issues

```bash
# View Celery logs
docker-compose logs celery

# Inspect active tasks
celery -A config inspect active

# Purge all pending tasks
celery -A config purge
```

### Docker Issues

```bash
# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check service status
docker-compose ps

# View full logs
docker-compose logs -f
```

### Database Migration Issues

```bash
# Makemigrations
python manage.py makemigrations

# Show pending migrations
python manage.py showmigrations

# Migrate specific app
python manage.py migrate users

# Rollback migration
python manage.py migrate users 0001
```

### Email Not Sending

```bash
# Test email configuration
python manage.py shell

>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
1  # Returns 1 if successful

# Check email backend in settings
# Check credentials in .env
# Check Gmail app password (if using Gmail)
```

### Static Files Issues

```bash
# Collect static files
python manage.py collectstatic --noinput

# Docker: Rebuild
docker-compose up -d --build
```

---

## Deployment Checklist

- [ ] Update `SECRET_KEY` in production
- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Setup SSL/TLS certificates
- [ ] Configure email backend
- [ ] Setup database backups
- [ ] Configure Redis persistence
- [ ] Enable logging and monitoring
- [ ] Setup error tracking (Sentry)
- [ ] Configure CDN for static files
- [ ] Setup automated deployments
- [ ] Test disaster recovery

---

## Useful Commands

```bash
# Development
python manage.py runserver
python manage.py createsuperuser
python manage.py makemigrations
python manage.py migrate

# Testing
pytest
pytest --cov=apps
pytest -v apps/users/tests/

# Database
python manage.py dbshell
python manage.py dumpdata > backup.json
python manage.py loaddata backup.json

# Cache
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()

# Celery
celery -A config worker -l info
celery -A config beat -l info

# Docker
docker-compose up -d
docker-compose down
docker-compose logs -f web
docker-compose exec web python manage.py migrate
```

---

## Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [SimpleJWT Documentation](https://django-rest-framework-simplejwt.readthedocs.io/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [drf-spectacular](https://drf-spectacular.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)

---

## License

This project is licensed under the MIT License.

---

## Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review application logs
3. Check Docker/service status
4. Submit issues on repository

---

**Last Updated:** August 2026
