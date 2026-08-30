import pytest
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


# ---------------------------
# Signup
# ---------------------------

@pytest.mark.django_db
def test_signup_view_creates_user(api_client):

    data = {
        "email": "newuser@example.com",
        "password": "StrongPass123!",
        "first_name": "Farhan",
        "last_name": "Kabir",
        "roles": "Customer"
    }

    response = api_client.post(
        "/user/signup/", data, format="json"
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(email="newuser@example.com").exists()


@pytest.mark.django_db
def test_signup_view_rejects_duplicate_email(api_client, customer):

    data = {
        "email": "customer@example.com",
        "password": "StrongPass123!",
        "first_name": "Farhan",
        "last_name": "Kabir",
        "roles": "Customer"
    }

    response = api_client.post(
        "/user/signup/", data, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_signup_view_rejects_invalid_phone_number(api_client):

    data = {
        "email": "badphoneview@example.com",
        "password": "StrongPass123!",
        "phone_number": "notanumber",
        "first_name": "Farhan",
        "last_name": "Kabir",
        "roles": "Customer"
    }

    response = api_client.post(
        "/user/signup/", data, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_signup_view_does_not_require_authentication(api_client):

    data = {
        "email": "openaccess@example.com",
        "password": "StrongPass123!",
        "first_name": "Farhan",
        "last_name": "Kabir",
        "roles": "Customer"
    }

    response = api_client.post(
        "/user/signup/", data, format="json"
    )

    assert response.status_code == status.HTTP_201_CREATED


# ---------------------------
# Login
# ---------------------------

@pytest.mark.django_db
def test_login_view_valid_credentials_returns_tokens(api_client, customer):

    data = {
        "email": "customer@example.com",
        "password": "StrongPass123!",
        "first_name": "Farhan",
        "last_name": "Kabir",
        "roles": "Customer"
    }

    response = api_client.post(
        "/user/login/", data, format="json"
    )

    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_login_view_wrong_password_returns_400(api_client, customer):

    data = {
        "email": "customer@example.com",
        "password": "WrongPassword!",
        "first_name": "Farhan",
        "last_name": "Kabir",
        "roles": "Customer"
    }

    response = api_client.post(
        "/user/login/", data, format="json"
    )

    # UserLoginSerializer.validate() raises a plain ValidationError,
    # which DRF's is_valid(raise_exception=True) surfaces as 400, not 401.
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_login_view_nonexistent_email_returns_400(api_client):

    data = {
        "email": "ghost@example.com",
        "password": "StrongPass123!",
        "first_name": "Farhan",
        "last_name": "Kabir",
        "roles": "Customer"
    }

    response = api_client.post(
        "/user/login/", data, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


# ---------------------------
# Logout
# ---------------------------

@pytest.mark.django_db
def test_logout_view_requires_authentication(api_client):

    response = api_client.post(
        "/user/logout/", {"refresh_token": "irrelevant"}, format="json"
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_logout_view_valid_token_returns_200(api_client, customer):

    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(customer)

    api_client.force_authenticate(user=customer)

    response = api_client.post(
        "/user/logout/",
        {"refresh_token": str(refresh)},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_logout_view_invalid_token_returns_400(api_client, customer):

    api_client.force_authenticate(user=customer)

    response = api_client.post(
        "/user/logout/",
        {"refresh_token": "not-a-real-token"},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


# ---------------------------
# Refresh Token
# ---------------------------

@pytest.mark.django_db
def test_refresh_view_valid_token_returns_access_token(api_client, customer):

    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(customer)

    response = api_client.post(
        "/user/refresh-token/",
        {"refresh_token": str(refresh)},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.data


@pytest.mark.django_db
def test_refresh_view_missing_token_returns_400(api_client):

    response = api_client.post(
        "/user/refresh-token/", {}, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_refresh_view_invalid_token_returns_401(api_client):

    response = api_client.post(
        "/user/refresh-token/",
        {"refresh_token": "garbage-token"},
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED