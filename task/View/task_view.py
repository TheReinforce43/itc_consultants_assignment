from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from task.Serializer.task_serializer import TaskSerializer
from task.Model.task_model import TaskModel
from utils import TaskPermission

class TaskViewSet(ModelViewSet):

    queryset = TaskModel.objects.select_related("createdBy")
    serializer_class = TaskSerializer

    permission_classes = [
        IsAuthenticated,
        TaskPermission,
    ]

    def perform_create(self, serializer):
        serializer.save(createdBy=self.request.user)