from rest_framework.permissions import BasePermission
from django.utils import timezone
from rest_framework.permissions import BasePermission


""""
For Testing purpose , I have includes here ,
RBAC : Role Based Access Control 
ABAC : Attribute Based Access Control


"""
class TaskPermission(BasePermission):

    WRITE_METHODS = ["POST", "PUT", "PATCH", "DELETE"]

    def has_permission(self, request, view):

        # User must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # ABAC: after 6 PM, no one can create/update/delete — read only
        current_hour = timezone.localtime(timezone.now()).hour
        if current_hour >= 18 and request.method in self.WRITE_METHODS:
            return False

        # Admin can do everything (subject to the time gate above)
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


