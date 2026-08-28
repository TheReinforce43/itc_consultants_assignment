from task.Serializer.task_serializer import TaskSerializer
import pytest


@pytest.mark.django_db
def test_task_serializer(task):

    serializer = TaskSerializer(task)

    assert serializer.data["title"] == "Test Task"

    assert (
        serializer.data["description"]
        == "Test task description"
    )

    assert (
        serializer.data["createdBy"]
        == "staff@example.com"
    )


@pytest.mark.django_db
def test_task_serializer_valid_data():

    data = {
        "title": "New Task",
        "description": "New task description",
    }

    serializer = TaskSerializer(data=data)

    assert serializer.is_valid()

    assert serializer.validated_data["title"] == "New Task"

    assert (
        serializer.validated_data["description"]
        == "New task description"
    )

@pytest.mark.django_db
def test_task_serializer_title_required():

    data = {
        "description": "Task description",
    }

    serializer = TaskSerializer(data=data)

    assert not serializer.is_valid()

    assert "title" in serializer.errors