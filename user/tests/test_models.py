import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_create_user_successful():

    user = User.objects.create_user(
        email="john@example.com",
        password="StrongPass123!",
    )

    assert user.email == "john@example.com"
    assert user.check_password("StrongPass123!")
    assert user.is_active
    assert not user.is_staff
    assert not user.is_superuser


@pytest.mark.django_db
def test_email_is_username_field():

    assert User.USERNAME_FIELD == "email"
    assert User.REQUIRED_FIELDS == []


@pytest.mark.django_db
def test_default_role_is_customer():

    user = User.objects.create_user(
        email="defaultrole@example.com",
        password="StrongPass123!",
    )

    assert user.roles == "Customer"


@pytest.mark.django_db
def test_customer_fixture_has_customer_role(customer):

    assert customer.roles == "Customer"


@pytest.mark.django_db
def test_staff_fixture_has_staff_role(staff):

    assert staff.roles == "Staff"


@pytest.mark.django_db
def test_admin_fixture_is_superuser(admin):

    assert admin.is_superuser
    assert admin.is_staff


@pytest.mark.django_db
def test_invalid_role_fails_full_clean_validation():

    user = User(
        email="badrole@example.com",
        roles="NotARealRole",
    )
    user.set_password("StrongPass123!")

    with pytest.raises(ValidationError):
        user.full_clean()


@pytest.mark.django_db
def test_email_must_be_unique(customer):

    with pytest.raises(IntegrityError):
        User.objects.create_user(
            email="customer@example.com",
            password="AnotherPass123!",
        )


@pytest.mark.django_db
def test_phone_number_can_be_null():

    user = User.objects.create_user(
        email="nophone@example.com",
        password="StrongPass123!",
    )

    assert user.phone_number is None


@pytest.mark.django_db
def test_profile_image_can_be_null():

    user = User.objects.create_user(
        email="noimage@example.com",
        password="StrongPass123!",
    )

    assert not user.profile_image


@pytest.mark.django_db
def test_str_returns_email(customer):

    assert str(customer) == "customer@example.com"


@pytest.mark.django_db
def test_password_is_hashed_not_plaintext(customer):

    assert customer.password != "StrongPass123!"
    assert customer.check_password("StrongPass123!")