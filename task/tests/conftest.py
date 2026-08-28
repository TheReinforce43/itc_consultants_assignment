import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from task.Model.task_model import TaskModel

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def customer(db):
    return User.objects.create_user(
        email="customer@example.com",
        password="StrongPass123!",
        roles="Customer",
    )


@pytest.fixture
def staff(db):
    return User.objects.create_user(
        email="staff@example.com",
        password="StrongPass123!",
        roles="Staff",
    )


@pytest.fixture
def admin(db):
    return User.objects.create_superuser(
        email="admin@example.com",
        password="StrongPass123!",
    )


@pytest.fixture
def task(db, staff):
    return TaskModel.objects.create(
        title="Test Task",
        description="Test task description",
        createdBy=staff,
    )