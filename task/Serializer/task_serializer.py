from rest_framework import serializers
from task.Model.task_model import TaskModel


class TaskSerializer(serializers.ModelSerializer):

    createdBy = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = TaskModel
        fields = [
            "id",
            "title",
            "description",
            "createdBy",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "createdBy",
            "created_at",
            "updated_at",
        ]