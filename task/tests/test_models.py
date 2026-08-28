import pytest
from task.Model.task_model import TaskModel



@pytest.mark.django_db
def test_task_created_successfully(task):

    assert task.title == "Test Task"

    assert task.description == "Test task description"

    assert task.createdBy.email == "staff@example.com"


@pytest.mark.django_db
def test_task_str(task):

    assert str(task) == "Test Task"


@pytest.mark.django_db
def test_task_created_by_staff(task, staff):

    assert task.createdBy == staff