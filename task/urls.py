from rest_framework.routers import DefaultRouter

from task.View.task_view import TaskViewSet

router = DefaultRouter()

router.register(
    r"tasks",
    TaskViewSet,
    basename="task"
)

# since here we are using DefaultRouter, we don't need to define the urlpatterns manually. The router will automatically generate the URL patterns for our viewset.
urlpatterns = router.urls