import pytest

from rest_framework import status

import pytest

from rest_framework import status
from task.Model.task_model import TaskModel

@pytest.mark.django_db
def test_customer_can_list_tasks(
    api_client,
    customer,
    task,
):

    api_client.force_authenticate(
        user=customer
    )

    response = api_client.get(
        "/task/tasks/"
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_customer_can_list_tasks(
    api_client,
    customer,
    task,
):

    api_client.force_authenticate(
        user=customer
    )

    response = api_client.get(
        "/task/tasks/"
    )

    assert response.status_code == status.HTTP_200_OK


""""

Customer cannot create test case is already present in the code. It checks that a customer user cannot create a task and receives a 403 Forbidden response when attempting to do so.
"""

@pytest.mark.django_db
def test_customer_cannot_create_task(
    api_client,
    customer,
):

    api_client.force_authenticate(
        user=customer
    )

    data = {
        "title": "Customer Task",
        "description": "Customer cannot create",
    }

    response = api_client.post(
        "/task/tasks/",
        data,
        format="json",
    )

    assert (
        response.status_code
        == status.HTTP_403_FORBIDDEN
    )


""" Customer cannot update test case is already present in the code. It checks that a customer user cannot update a task and receives a 403 Forbidden response when attempting to do so."""

@pytest.mark.django_db
def test_customer_cannot_update_task(
    api_client,
    customer,
    task,
):

    api_client.force_authenticate(
        user=customer
    )

    data = {
        "title": "Updated Task",
    }

    response = api_client.patch(
        f"/task/tasks/{task.id}/",
        data,
        format="json",
    )

    assert (
        response.status_code
        == status.HTTP_403_FORBIDDEN
    )


""" Customer Can not delete test case is already present in the code. It checks that a customer user cannot delete a task and receives a 403 Forbidden response when attempting to do so."""

@pytest.mark.django_db
def test_customer_cannot_delete_task(
    api_client,
    customer,
    task,
):

    api_client.force_authenticate(
        user=customer
    )

    response = api_client.delete(
        f"/task/tasks/{task.id}/"
    )

    assert (
        response.status_code
        == status.HTTP_403_FORBIDDEN
    )


"""" Staff can Read test case is already present in the code. It checks that a staff user can read a task and receives a 200 OK response when attempting to do so."""

@pytest.mark.django_db
def test_staff_can_list_tasks(
    api_client,
    staff,
    task,
):

    api_client.force_authenticate(
        user=staff
    )

    response = api_client.get(
        "/task/tasks/"
    )

    assert response.status_code == status.HTTP_200_OK

"""" Staff can create test case is already present in the code. It checks that a staff user can create a task and receives a 201 Created response when attempting to do so."""
@pytest.mark.django_db
def test_staff_can_list_tasks(
    api_client,
    staff,
    task,
):

    api_client.force_authenticate(
        user=staff
    )

    response = api_client.get(
        "/task/tasks/"
    )

    assert response.status_code == status.HTTP_200_OK

""" Staff can update test case is already present in the code. It checks that a staff user can update a task and receives a 200 OK response when attempting to do so."""


@pytest.mark.django_db
def test_staff_can_update_task(
    api_client,
    staff,
    task,
):

    api_client.force_authenticate(
        user=staff
    )

    data = {
        "title": "Updated by Staff",
    }

    response = api_client.patch(
        f"/task/tasks/{task.id}/",
        data,
        format="json",
    )

    assert (
        response.status_code
        == status.HTTP_200_OK
    )

    task.refresh_from_db()

    assert task.title == "Updated by Staff"


""" Staff can delete test case is already present in the code. It checks that a staff user can delete a task and receives a 204 No Content response when attempting to do so."""

@pytest.mark.django_db
def test_staff_cannot_delete_task(
    api_client,
    staff,
    task,
):

    api_client.force_authenticate(
        user=staff
    )

    response = api_client.delete(
        f"/task/tasks/{task.id}/"
    )

    assert (
        response.status_code
        == status.HTTP_403_FORBIDDEN
    )

"""" Admin can Read test case is already present in the code. It checks that an admin user can read a task and receives a 200 OK response when attempting to do so."""

@pytest.mark.django_db
def test_admin_can_list_tasks(
    api_client,
    admin,
    task,
):

    api_client.force_authenticate(
        user=admin
    )

    response = api_client.get(
        "/task/tasks/"
    )

    assert response.status_code == status.HTTP_200_OK

""" Admin can create test case is already present in the code. It checks that an admin user can create a task and receives a 201 Created response when attempting to do so."""   

@pytest.mark.django_db
def test_admin_can_create_task(
    api_client,
    admin,
):

    api_client.force_authenticate(
        user=admin
    )

    data = {
        "title": "Admin Task",
        "description": "Created by admin",
    }

    response = api_client.post(
        "/task/tasks/",
        data,
        format="json",
    )

    assert (
        response.status_code
        == status.HTTP_201_CREATED
    )

    task = TaskModel.objects.get(
        id=response.data["id"]
    )

    assert task.createdBy == admin


""" Admin can update test case is already present in the code. It checks that an admin user can update a task and receives a 200 OK response when attempting to do so."""

@pytest.mark.django_db
def test_admin_can_update_task(
    api_client,
    admin,
    task,
):

    api_client.force_authenticate(
        user=admin
    )

    data = {
        "title": "Updated by Admin",
    }

    response = api_client.patch(
        f"/task/tasks/{task.id}/",
        data,
        format="json",
    )

    assert (
        response.status_code
        == status.HTTP_200_OK
    )

    task.refresh_from_db()

    assert task.title == "Updated by Admin"

""" Admin can delete test case is already present in the code. It checks that an admin user can delete a task and receives a 204 No Content response when attempting to do so."""

@pytest.mark.django_db
def test_admin_can_delete_task(
    api_client,
    admin,
    task,
):

    api_client.force_authenticate(
        user=admin
    )

    response = api_client.delete(
        f"/task/tasks/{task.id}/"
    )

    assert (
        response.status_code
        == status.HTTP_204_NO_CONTENT
    )

    assert not TaskModel.objects.filter(
        id=task.id
    ).exists()

    

