import pytest
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.contrib.auth import get_user_model

from user.Serializer.user_serializer import (
    UserSignUpSerializer,
    UserLoginSerializer,
    UserLogoutSerializer,
    GetUserSerializer,
)

User = get_user_model()


# ---------------------------
# UserSignUpSerializer
# ---------------------------

@pytest.mark.django_db
def test_signup_serializer_valid_minimal_data():

    data = {
        "email": "signup1@example.com",
        "password": "StrongPass123!",
    }

    serializer = UserSignUpSerializer(data=data)

    assert serializer.is_valid(), serializer.errors

    user = serializer.save()

    assert user.email == "signup1@example.com"
    assert user.check_password("StrongPass123!")


@pytest.mark.django_db
def test_signup_serializer_valid_with_phone_number():

    data = {
        "email": "signup2@example.com",
        "password": "StrongPass123!",
        "phone_number": "1234567890",
    }

    serializer = UserSignUpSerializer(data=data)

    assert serializer.is_valid(), serializer.errors

    user = serializer.save()

    assert user.phone_number == "1234567890"


@pytest.mark.django_db
def test_signup_serializer_password_is_write_only():

    data = {
        "email": "writeonly@example.com",
        "password": "StrongPass123!",
    }

    serializer = UserSignUpSerializer(data=data)
    serializer.is_valid()

    assert "password" not in serializer.data


@pytest.mark.django_db
def test_signup_serializer_rejects_non_digit_phone_number():

    data = {
        "email": "badphone@example.com",
        "password": "StrongPass123!",
        "phone_number": "abc1234567",
    }

    serializer = UserSignUpSerializer(data=data)

    assert not serializer.is_valid()
    assert "phone_number" in serializer.errors


@pytest.mark.django_db
def test_signup_serializer_rejects_too_short_phone_number():

    data = {
        "email": "shortphone@example.com",
        "password": "StrongPass123!",
        "phone_number": "12345",
    }

    serializer = UserSignUpSerializer(data=data)

    assert not serializer.is_valid()
    assert "phone_number" in serializer.errors


@pytest.mark.django_db
def test_signup_serializer_rejects_too_long_phone_number():

    data = {
        "email": "longphone@example.com",
        "password": "StrongPass123!",
        "phone_number": "1" * 16,
    }

    serializer = UserSignUpSerializer(data=data)

    assert not serializer.is_valid()
    assert "phone_number" in serializer.errors


@pytest.mark.django_db
def test_signup_serializer_rejects_duplicate_phone_number():

    User.objects.create_user(
        email="firstphone@example.com",
        password="StrongPass123!",
        phone_number="1112223333",
    )

    data = {
        "email": "secondphone@example.com",
        "password": "StrongPass123!",
        "phone_number": "1112223333",
    }

    serializer = UserSignUpSerializer(data=data)

    assert not serializer.is_valid()
    assert "phone_number" in serializer.errors


@pytest.mark.django_db
def test_signup_serializer_rejects_duplicate_email(customer):

    data = {
        "email": "customer@example.com",
        "password": "StrongPass123!",
    }

    serializer = UserSignUpSerializer(data=data)

    assert not serializer.is_valid()
    assert "email" in serializer.errors


@pytest.mark.django_db
def test_signup_serializer_requires_email():

    data = {
        "password": "StrongPass123!",
    }

    serializer = UserSignUpSerializer(data=data)

    assert not serializer.is_valid()
    assert "email" in serializer.errors


# ---------------------------
# UserLoginSerializer
# ---------------------------

@pytest.mark.django_db
def test_login_serializer_valid_credentials_returns_tokens(customer):

    data = {
        "email": "customer@example.com",
        "password": "StrongPass123!",
    }

    serializer = UserLoginSerializer(data=data)

    assert serializer.is_valid(), serializer.errors
    assert "access" in serializer.validated_data
    assert "refresh" in serializer.validated_data
    assert serializer.validated_data["email"] == "customer@example.com"
    assert serializer.validated_data["roles"] == "Customer"


@pytest.mark.django_db
def test_login_serializer_wrong_password_raises_validation_error(customer):

    data = {
        "email": "customer@example.com",
        "password": "WrongPassword!",
    }

    serializer = UserLoginSerializer(data=data)

    with pytest.raises(DRFValidationError):
        serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_login_serializer_nonexistent_email_raises_validation_error():

    data = {
        "email": "doesnotexist@example.com",
        "password": "StrongPass123!",
    }

    serializer = UserLoginSerializer(data=data)

    with pytest.raises(DRFValidationError):
        serializer.is_valid(raise_exception=True)


# ---------------------------
# UserLogoutSerializer
# ---------------------------

@pytest.mark.django_db
def test_logout_serializer_blacklists_valid_refresh_token(customer):

    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(customer)

    serializer = UserLogoutSerializer(
        data={"refresh_token": str(refresh)}
    )

    assert serializer.is_valid(), serializer.errors

    serializer.save()  # should not raise


@pytest.mark.django_db
def test_logout_serializer_invalid_token_raises_error(customer):

    serializer = UserLogoutSerializer(
        data={"refresh_token": "not-a-real-token"}
    )

    assert serializer.is_valid(), serializer.errors

    with pytest.raises(DRFValidationError):
        serializer.save()


# ---------------------------
# GetUserSerializer
# ---------------------------

@pytest.mark.django_db
def test_get_user_serializer_returns_expected_fields(customer):

    serializer = GetUserSerializer(customer)

    assert serializer.data["email"] == "customer@example.com"
    assert serializer.data["roles"] == "Customer"
    assert "password" not in serializer.data