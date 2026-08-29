import pytest

from rest_framework import status


@pytest.mark.django_db
def test_unauthenticated_user_cannot_access_tasks(
    api_client,
):

    response = api_client.get("/task/tasks/")

    assert (
        response.status_code
        == status.HTTP_401_UNAUTHORIZED
    )



@pytest.mark.django_db
def test_authenticated_user_can_access_tasks(
    api_client,
    customer,
):

    api_client.force_authenticate(
        user=customer
    )
    response = api_client.get("/task/tasks/")

    assert response.status_code == status.HTTP_200_OK