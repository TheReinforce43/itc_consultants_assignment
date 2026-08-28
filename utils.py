from rest_framework.permissions import BasePermission


class TaskPermission(BasePermission):

    def has_permission(self, request, view):

        # User must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # Admin can do everything
        if request.user.is_superuser:
            return True

        # Customer can only read
        if request.user.roles == "Customer":
            return request.method in ["GET", "HEAD", "OPTIONS"]

        # Staff can read, create and update
        if request.user.roles == "Staff":
            return request.method in [
                "GET",
                "HEAD",
                "OPTIONS",
                "POST",
                "PUT",
                "PATCH",
            ]

        return False

user_roles=(
    ('Admin','Admin'),
    ('Seller','Seller'),
    ('Customer','Customer')
)


